import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
from itertools import product
class DummyModel() :
    def __init__(self, name='') :
        self.name = name
        
class ScoreEval() :
    '''
    Main entrence for score evaluation. Create an instance of ScoreEval and run methods step by step. 
    '''
    def __init__(self, models, data=None, weight_cols=[]):
        self.scores = []
        self.models = models
        self.data = data
        self.metrics = []
        self.cutset = []
        self.ivset = []
        self.weight_cols = weight_cols
        # self.cmap = ['red', 'green', 'orange', 'blue', 'purple', 'pink', 'grey'] * 5
        self.cmap = [ 
                '#990066', 
                '#663333',
                '#FFCC00',
                '#33AA33',
                '#006699',
                '#FF7733',
                '#009999',
                '#CCCC00',
                '#663399',
                '#aa2211',
                '#003399',
                '#99CC00',
                '#663300',
                '#FFCCCC',
                '#666699',
            ] * 3
        
    def _initialize_plot(self, figsize=(16,8)) :
        
        fig, axes = plt.subplots(len(self.models),1, figsize=figsize)
        if type(axes) != np.ndarray : 
            return fig, np.array([axes])
        return fig, axes

    def run_score(self, X, Y, func=None) :
        '''
        X: The input data for your model. 
        Y: The input label of your data set. 
        func: customized predict function, take every model in self.models and X as input. 
        '''
        self.scores = []
        for model in self.models :
            if func :
                pred = func(model, X)
                # pred = pred.reshape((pred.shape[0], 1))
            else :
                pred = model.predict(X)
            pred = pd.DataFrame.from_records(pred)
            pred.columns=['score']
            pred['label'] = Y
            # final = Y.merge(pred, how='inner', left_index=True, right_index=True)
            if self.weight_cols :
                pred[self.weight_cols] = self.data[self.weight_cols]
            else :
                pred[['weight1', 'weight2']] = 1
            self.scores.append(pred)

    def run_score_breakdown(self, break_col=[], break_val=[], filter_col=[], fval=[], fops=lambda x,y: x==y, id_col='risk_channel_id', score_col='Webapp_trust_model_score', label_col='is_fraud', weight_cols=[None, 'event_amount'], score_scale=0.01) :
            scores = []
            cols = [break_col, filter_col, id_col, score_col, label_col]
            w1, w2 = weight_cols
            if w1 :
                cols.append(w1)
            if w2 :
                cols.append(w2)
            # Select columns
            data = self.data[cols].rename(
                columns={
                    id_col: 'id', score_col: 'score', label_col: 'label', w1: 'weight1',  w2: 'weight2'
                }
            )
            
            if score_scale :
                data['score'] = data['score'] * score_scale
                
            # Compute scores by every group     
            values = list(set(data[break_col].values.flatten().tolist()))
            
            for val in break_val :
                # break down
                df_scr = data.loc[data[break_col]==val, :]
                
                # filter 
                for fv in fval :
                    df_scr1 = df_scr.loc[fops(df_scr[filter_col],fv), :].copy()

                    if w1 is None :
                        df_scr1['weight1'] = 1
                    if w2 is None :
                        df_scr1['weight2'] = 1


                    print(f"break down by {val} with filter by {fv} : {df_scr1['score'].isnull().sum()} rows are null, {df_scr1['score'].notnull().sum()} not null.")

                    scores.append(
                        df_scr1[df_scr1['score'].notnull()]
                    )
            self.scores = scores
            return scores

    def score_cut(self, cut_step=0.02, buckets=100):
        '''
        Must run after self.run_score. cutoff and operating point will be generated. 
        Pre-assume the score is in interval [0,1], both result will be produced and saved in self attributes.
        cut_step: the step length by equal-width cut
        buckets: number of bins by equal-freq cut
        '''
        self.cutset = []
        self.opset  = []
        
        for eval_df in self.scores :
            # Evaluation on score cutoff
            cutoff = np.arange(0, 1, cut_step)
            pre_cut = []
            for c in cutoff :
                topc = eval_df.loc[eval_df['score'] > c, :]
                pre = topc.loc[topc['label']==1, 'weight1'].sum() / topc['weight1'].sum()
                rec = topc.loc[topc['label']==1, 'weight2'].sum() / (eval_df.loc[eval_df['label'] == 1, 'weight2']).sum()
         
                cut = c
                
                rlt0 = [pre, rec, cut, topc.shape[0], (topc['label'] == 1).sum(), (topc.loc[topc['label']==1, 'weight2'].sum())]
                pre_cut.append(rlt0)
            pre_cut = pd.DataFrame.from_records(pre_cut, columns = ['precision', 'recall', 'cutoff', 'captured', '1_captured', 'w2_captured']).reset_index()
            self.cutset.append(pre_cut)
            
            # Evaluation on Operation point. 
            ops = range(0, eval_df.shape[0], eval_df.shape[0] // buckets)
            eval_df1 = eval_df.sort_values('score', ascending=False)
            pre_df = [] # pd.DataFrame()
            for i in ops :
                if i == 0 :
                    continue
                topi = eval_df1.iloc[:i,]
                pre  = (topi.loc[topi['label'] == 1, 'weight1']).sum() / topi['weight1'].sum()
                
                rec  = (topi.loc[topi['label'] == 1, 'weight2']).sum() / (eval_df1.loc[eval_df1['label'] == 1, 'weight2']).sum()
                
                
                cut  = topi['score'].min()
                rlt0 = [pre, rec, cut, i, (topi['label'] == 1).sum(), (topi.loc[topi['label']==1, 'weight2'].sum())]
                
                pre_df.append(rlt0)
            pre_df = pd.DataFrame.from_records(pre_df)
            pre_df.columns=['precision', 'recall', 'cutoff', 'captured', '1_captured', 'w2_captured']
            pre_df = pre_df.reset_index()
            
            self.opset.append(pre_df)
            
    def daily_recall(self, figsize=(16,8), qtl_list = ['r99', 'r95', 'r90','r50',], x_step=2):
        
        fig, axes = self._initialize_plot(figsize=(figsize[0], figsize[1]*len(self.models)))
        
        for ax, data in zip(axes, self.scores) :
        
            data1 = data.copy()
            # tp : true positive
            data1['tp99'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.99, axis=1)
            data1['tp95'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.95, axis=1)
            data1['tp90'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.90, axis=1)
            data1['tp75'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.75, axis=1)
            data1['tp50'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.50, axis=1)
            data1['tp25'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.25, axis=1)
            data1['tp10'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.10, axis=1)
            data1['tp01'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.01, axis=1)
            # ap : all positive
            data1['ap99'] = data1.apply(lambda x : x['label']==1, axis=1)
            data1['ap95'] = data1.apply(lambda x : x['label']==1, axis=1)
            data1['ap90'] = data1.apply(lambda x : x['label']==1, axis=1)
            data1['ap75'] = data1.apply(lambda x : x['label']==1, axis=1)
            data1['ap50'] = data1.apply(lambda x : x['label']==1, axis=1)
            data1['ap25'] = data1.apply(lambda x : x['label']==1, axis=1)
            data1['ap10'] = data1.apply(lambda x : x['label']==1, axis=1)
            data1['ap01'] = data1.apply(lambda x : x['label']==1, axis=1)
            
            stats_bydate = data1.groupby('date').agg(pd.Series.sum).reset_index()
            
            stats_bydate['r99'] = stats_bydate.apply(lambda x : x['tp99'] / (x['ap99'] + 0.0001), axis=1)
            stats_bydate['r95'] = stats_bydate.apply(lambda x : x['tp95'] / (x['ap95'] + 0.0001), axis=1)
            stats_bydate['r90'] = stats_bydate.apply(lambda x : x['tp90'] / (x['ap90'] + 0.0001), axis=1)
            stats_bydate['r75'] = stats_bydate.apply(lambda x : x['tp75'] / (x['ap75'] + 0.0001), axis=1)
            stats_bydate['r50'] = stats_bydate.apply(lambda x : x['tp50'] / (x['ap50'] + 0.0001), axis=1)
            stats_bydate['r25'] = stats_bydate.apply(lambda x : x['tp25'] / (x['ap25'] + 0.0001), axis=1)
            stats_bydate['r10'] = stats_bydate.apply(lambda x : x['tp10'] / (x['ap10'] + 0.0001), axis=1)
            stats_bydate['r01'] = stats_bydate.apply(lambda x : x['tp01'] / (x['ap01'] + 0.0001), axis=1)
            
            ax.bar(stats_bydate['date'], stats_bydate['label'], color = 'lightsteelblue')

            
            date_axis = stats_bydate['date']
            
            ax.set_xticks([ i for i in range(0, len(date_axis), x_step) ])
            ax.set_xticklabels([ date_axis[i] for i in range(0, len(date_axis), x_step) ])
            plt.xticks(rotation=90)
            
            ax2 = ax.twinx()

            ax2.set_xticks([ i for i in range(0, len(date_axis), x_step) ])
            ax2.set_xticklabels([ date_axis[i] for i in range(0, len(date_axis), x_step) ])
            plt.xticks(rotation=90)

            date_axis = stats_bydate['date']

            handles = []
            for q in qtl_list :

                hdl, = ax2.plot(stats_bydate['date'], stats_bydate[q])
                handles.append(hdl)
            
            ax2.set_yticks(np.arange(0,1.02,0.02))
            ax2.grid(axis='y', linestyle='--')

            plt.legend(handles=handles, labels=qtl_list, loc='best')            
        plt.show()
        
    def daily_precision(self, figsize=(16,8), qtl_list = ['p99', 'p95', 'p90','p50',], x_step=2):
        fig, axes = self._initialize_plot(figsize=(figsize[0], figsize[1]*len(self.models)))

        for ax, data in zip(axes, self.scores) :
            data1 = data.copy()
            # tp : true positive
            data1['tp99'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.99, axis=1)
            data1['tp95'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.95, axis=1)
            data1['tp90'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.90, axis=1)
            data1['tp75'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.75, axis=1)
            data1['tp50'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.50, axis=1)
            data1['tp25'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.25, axis=1)
            data1['tp10'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.10, axis=1)
            data1['tp01'] = data1.apply(lambda x : x['label']==1 and x['score']>=0.01, axis=1)
            # sc : score cut
            data1['sc99'] = data1.apply(lambda x : x['score']>=0.99, axis=1)
            data1['sc95'] = data1.apply(lambda x : x['score']>=0.95, axis=1)
            data1['sc90'] = data1.apply(lambda x : x['score']>=0.90, axis=1)
            data1['sc75'] = data1.apply(lambda x : x['score']>=0.75, axis=1)
            data1['sc50'] = data1.apply(lambda x : x['score']>=0.50, axis=1)
            data1['sc25'] = data1.apply(lambda x : x['score']>=0.25, axis=1)
            data1['sc10'] = data1.apply(lambda x : x['score']>=0.10, axis=1)
            data1['sc01'] = data1.apply(lambda x : x['score']>=0.01, axis=1)
            
            stats_bydate = data1.groupby('date').agg(pd.Series.sum).reset_index()

            stats_bydate['p99'] = stats_bydate.apply(lambda x : x['tp99'] / (x['sc99'] + 0.0001), axis=1)
            stats_bydate['p95'] = stats_bydate.apply(lambda x : x['tp95'] / (x['sc95'] + 0.0001), axis=1)
            stats_bydate['p90'] = stats_bydate.apply(lambda x : x['tp90'] / (x['sc90'] + 0.0001), axis=1)
            stats_bydate['p75'] = stats_bydate.apply(lambda x : x['tp75'] / (x['sc75'] + 0.0001), axis=1)
            stats_bydate['p50'] = stats_bydate.apply(lambda x : x['tp50'] / (x['sc50'] + 0.0001), axis=1)
            stats_bydate['p25'] = stats_bydate.apply(lambda x : x['tp25'] / (x['sc25'] + 0.0001), axis=1)
            stats_bydate['p10'] = stats_bydate.apply(lambda x : x['tp10'] / (x['sc10'] + 0.0001), axis=1)
            stats_bydate['p01'] = stats_bydate.apply(lambda x : x['tp01'] / (x['sc01'] + 0.0001), axis=1)
            
            ax.bar(stats_bydate['date'], stats_bydate['label'], color = 'lightsteelblue')

            
            date_axis = stats_bydate['date']
            ax.set_xticks([ i for i in range(0, len(date_axis), x_step) ])
            ax.set_xticklabels([ date_axis[i] for i in range(0, len(date_axis), x_step) ])
         
            plt.xticks(rotation=90)
            
            ax2 = ax.twinx()

            ax2.set_xticks([ i for i in range(0, len(date_axis), x_step) ])
            ax2.set_xticklabels([ date_axis[i] for i in range(0, len(date_axis), x_step) ])

            plt.xticks(rotation=90)

            handles = []
            for q in qtl_list :

                hdl, = ax2.plot(stats_bydate['date'], stats_bydate[q])
                handles.append(hdl)
            
            ax2.set_yticks(np.arange(0,1.02,0.02))
            ax2.grid(axis='y', linestyle='--')

            plt.legend(handles=handles, labels=qtl_list, loc='best')            
        plt.show()


    def daily_qtls(self, figsize=(16,8), qtl_list = ['q99', 'q95', 'q90','q75','q50', 'q25','q10','q01'], x_step=2 ) :
        
        fig, axes = self._initialize_plot(figsize=(figsize[0], figsize[1]*len(self.models)))
        for ax, data in zip(axes, self.scores) :
            stats_bydate = data.groupby('date').agg({
                'label': pd.Series.sum, 
                'score': [lambda x: np.quantile(x, 0.99), lambda x: np.quantile(x, 0.95), lambda x: np.quantile(x, 0.9), 
                          lambda x: np.quantile(x, 0.75),  lambda x: np.quantile(x, 0.5), lambda x: np.quantile(x, 0.25),
                          lambda x: np.quantile(x, 0.1), lambda x: np.quantile(x, 0.01)
                         ]
            #     'score': [lambda x: sum(x > 0.99), lambda x: sum(x > 0.9), lambda x: sum(x > 0.8), lambda x: sum(x > 0.99)]
            }).reset_index()
            stats_bydate.columns = [
                'date',
                'label_cnt', 
                'q99', 
                'q95', 
                'q90',
                'q75',
                'q50', 
                'q25',
                'q10',
                'q01'
            ]
            
            ax.bar(stats_bydate['date'], stats_bydate['label_cnt'], color = 'lightsteelblue')

            date_axis = stats_bydate['date'].unique()
            
            ax.set_xticks([ i for i in range(0, len(date_axis), x_step) ])
            ax.set_xticklabels([ date_axis[i] for i in range(0, len(date_axis), x_step) ])
         
            plt.xticks(rotation=90)
            
            ax2 = ax.twinx()

            ax2.set_xticks([ i for i in range(0, len(date_axis), x_step) ])
            ax2.set_xticklabels([ date_axis[i] for i in range(0, len(date_axis), x_step) ])

            plt.xticks(rotation=90)

            handles = []
            for q in qtl_list :

                hdl, =ax2.plot(stats_bydate['date'], stats_bydate[q])
                handles.append(hdl)

            ax2.set_yticks(np.arange(0,1.02,0.02))
            ax2.set_ylim(0,1.02)
            ax2.grid(axis='y', linestyle='--')


            plt.legend(handles=handles, labels=qtl_list, loc='best')            
        plt.show()
    
    def iv(self, bins=20, plot=True, figsize=(10, 10), bin_col='score_bin') :

        fig, axes = self._initialize_plot(figsize=(figsize[0], figsize[1]*len(self.models)))
        
        for ax, data in zip(axes, self.scores) :
            # score distribution
            data_final_1 = data.assign(
                score_bin = pd.cut(data['score'], bins),
                score_qtl = pd.qcut(data['score'], bins),
            )

            N0 = (data_final_1['label'] == 0).sum()
            N1 = (data_final_1['label'] == 1).sum()

            
            data_final_2 = data_final_1.groupby(bin_col).agg({
                'label' : [pd.Series.count, pd.Series.sum]
            })

            data_final_2.columns = ['cnt', 'inc']

            data_final_2 = data_final_2.reset_index()
            data_final_2 = data_final_2.assign(
                woe = lambda x: np.log(x['inc'] / N1) - np.log((x['cnt'] - x['inc'] ) / N0),
                binbd = data_final_2[bin_col].apply(lambda x: x.right),
            )

            score_iv = np.sum((data_final_2['inc'] / N1 - (data_final_2['cnt'] - data_final_2['inc'])/ N0) * data_final_2['woe'])
            
            self.ivset.append(score_iv)
            
            if plot :
                cmap = self.cmap
                ax.bar( data_final_2.index, data_final_2['woe'], color=(data_final_2['woe']<=0).astype(int).apply(lambda x: cmap[x]))
                ax.set_xticklabels(data_final_2['binbd'])
                ax.set_title('IV:{}'.format(score_iv))
    
    def score_distribution(self, bins=20, plot=True, figsize=(10, 10), bin_col='score_bin') :

        fig, axes = self._initialize_plot(figsize=(figsize[0], figsize[1]*len(self.models)))
        
        for ax, data in zip(axes, self.scores) :
            # score distribution
            data_final_1 = data.assign(
                score_bin = pd.cut(data['score'], bins),
                score_qtl = pd.qcut(data['score'], bins),
            )

            
            data_final_2 = data_final_1.groupby(bin_col).agg({
                'label' : [pd.Series.count, pd.Series.sum]
            })

            data_final_2.columns = ['cnt', 'inc']

            data_final_2 = data_final_2.reset_index()
            data_final_2 = data_final_2.assign(
                binbd = data_final_2[bin_col].apply(lambda x: x.right),
            )
            
            if plot :
                cmap = self.cmap
                ax.bar( data_final_2.index, data_final_2['cnt'], color=cmap[2])
        
    def plot_cutoff_chart(self, index_col=None, x_step=2, xlim=(0,100), ylim=(0,1.02), save_path=None, figsize=(10,10), chunksize=None) :   
        
        chunksize = len(self.opset) if chunksize is None else chunksize
        
        for i in range(0, len(self.opset), chunksize) :
            
            md_names = [ m.name for m in self.models[i:i+chunksize] ]
            fig, ax = plt.subplots(1,1, figsize=figsize)
            ax.ylim=ylim
            ax.y_ticks=ylim

            ax2 = ax.twinx()
            handles = []
            for pre_df, c in zip(self.cutset[i:i+chunksize], self.cmap[:chunksize]) :

                pre_df = pre_df.head(xlim[1])

                p1, = ax.plot(pre_df.loc[:, 'precision'].fillna(0), color=c)

                p2, = ax2.plot(pre_df.loc[:, 'recall'].fillna(0),  linestyle='--', color=c)

                handles.extend([p1, p2])

            ax.set_ylabel('precision')
            ax.set_xlim(*xlim)
            ax.set_xticks(range(0, pre_df.shape[0], x_step))
            ax.grid(which='both', axis='both')

            ax2.set_ylabel('recall')
            ax2.set_xlim(*xlim)
            ax2.grid(which='both', axis='both', linestyle='--')


            plt.legend(handles=handles, labels=product(md_names, ['precision', 'recall']), loc='best')            

            if index_col:
                ax.set_xticklabels(pre_df[index_col].map(lambda x: round(x,2)).iloc[0: pre_df.shape[0]+1:x_step])
            plt.xticks(rotation=90)

            if save_path: 
                plt.savefig(save_path)
            else :
                plt.show()
            plt.close()
        
    def plot_op_chart(self, index_col=None, x_step=2, xlim=(0,100), ylim=(0,1.02), save_path=None, figsize=(10,10), chunksize=None) :
        
        chunksize = len(self.opset) if chunksize is None else chunksize
        
        for i in range(0, len(self.opset), chunksize) :
            
            md_names = [ m.name for m in self.models[i:i+chunksize] ]
            fig, ax = plt.subplots(1,1, figsize=figsize)
            ax.ylim=ylim
            ax.y_ticks=ylim

            ax2 = ax.twinx()
            handles = []
            for pre_df, c in zip(self.opset[i:i+chunksize], self.cmap[:chunksize]) :

                pre_df = pre_df.head(xlim[1])

                p1, = ax.plot(pre_df.loc[:, 'precision'].fillna(0), color=c)

                p2, = ax2.plot(pre_df.loc[:, 'recall'].fillna(0),  linestyle='--', color=c)

                handles.extend([p1, p2])

            ax.set_ylabel('precision')
            ax.set_xlim(*xlim)
            ax.set_xticks(range(0, pre_df.shape[0], x_step))
            ax.grid(which='both', axis='both')

            ax2.set_ylabel('recall')
            ax2.set_xlim(*xlim)
            ax2.grid(which='both', axis='both', linestyle='--')


            plt.legend(handles=handles, labels=product(md_names, ['precision', 'recall']), loc='best')            

            if index_col:
                ax.set_xticklabels(pre_df[index_col].map(lambda x: round(x,2)).iloc[0: pre_df.shape[0]+1:x_step])
            plt.xticks(rotation=90)

            if save_path: 
                plt.savefig(save_path)
            else :
                plt.show()
            plt.close()

    def plot_pr(self, tick_step=0.02, save_path=None, figsize=(10,10)) :
        
        fig, ax = plt.subplots(1,1, figsize=figsize)
        
        ax.ylim=(0,1)
        ax.y_ticks=(0,1)
        
        handles = []
        for pre_df in self.opset :
            p1, = ax.plot(
                pre_df.loc[(~pre_df['recall'].isnull()) & (pre_df['recall']>0.0), 'recall'],
                pre_df.loc[(~pre_df['precision'].isnull()) & (pre_df['precision']>0.0), 'precision']
            )
            handles.append(p1)
            
        ax.set_ylabel('precision')
        ax.set_xlabel('recall')
        ax.set_xlim(0,1.02)
        ax.set_ylim(0,1.02)
        ax.grid(which='both', axis='both')
        
        plt.legend(handles=handles, labels=[ m.name for m in self.models ], loc='best')     
        
        if save_path: 
            plt.savefig(save_path)
        else :
            plt.show()
        plt.close()



class ScoreEvalNegative(ScoreEval) :

    def score_cut(self, cut_step=0.02, buckets=100):
        '''
        Must run after self.run_score. cutoff and operating point will be generated. 
        Pre-assume the score is in interval [0,1], both result will be produced and saved in self attributes.
        cut_step: the step length by equal-width cut
        buckets: number of bins by equal-freq cut
        '''
        self.cutset = []
        self.opset  = []
        
        for eval_df in self.scores :
            # Evaluation on score cutoff
            cutoff = np.arange(0, 1, cut_step)
            pre_cut = []
            for c in cutoff :
                topc = eval_df.loc[eval_df['score'] < c, :]
                pre = topc.loc[topc['label']==1, 'weight1'].sum() / topc['weight1'].sum()
                rec = topc.loc[topc['label']==1, 'weight2'].sum() / (eval_df.loc[eval_df['label'] == 1, 'weight2']).sum()
         
                cut = c
                
                rlt0 = [pre, rec, cut, topc.shape[0], (topc['label'] == 1).sum(), (topc.loc[topc['label']==1, 'weight2'].sum())]
                pre_cut.append(rlt0)
            pre_cut = pd.DataFrame.from_records(pre_cut, columns = ['precision', 'recall', 'cutoff', 'captured', '1_captured', 'w2_captured']).reset_index()
            self.cutset.append(pre_cut)
            
            # Evaluation on Operation point. 
            ops = range(0, eval_df.shape[0], eval_df.shape[0] // buckets)
            eval_df1 = eval_df.sort_values('score', ascending=True)
            pre_df = [] # pd.DataFrame()
            for i in ops :
                if i == 0 :
                    continue
                topi = eval_df1.iloc[:i,]
                pre  = (topi.loc[topi['label'] == 1, 'weight1']).sum() / topi['weight1'].sum()
                
                rec  = (topi.loc[topi['label'] == 1, 'weight2']).sum() / (eval_df1.loc[eval_df1['label'] == 1, 'weight2']).sum()
                
                
                cut  = topi['score'].max()
                rlt0 = [pre, rec, cut, i, (topi['label'] == 1).sum(), (topi.loc[topi['label']==1, 'weight2'].sum())]
                
                pre_df.append(rlt0)
            pre_df = pd.DataFrame.from_records(pre_df)
            pre_df.columns=['precision', 'recall', 'cutoff', 'captured', '1_captured', 'w2_captured']
            pre_df = pre_df.reset_index()
            
            self.opset.append(pre_df)
