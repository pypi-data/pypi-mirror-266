import pandas as pd
from redrel import MetricBase
from preprocess import get_woe_df
import pickle, json
class ModelBase(MetricBase) :
    '''
    We define ModelBase for the objects who need both fit and transform phases. 
    Eg. Some binning/normalization techniques need to save the mapping or mean/std value so to apply on future data. 
    They need to call `fit` at first to learn the parameters and then call `transform` to apply the transformation in new dataset. 
    '''
    def __init__(self, data, xcols=..., ycols=..., *args, **kwargs):
    
        super().__init__(data, xcols, ycols, *args, **kwargs)

    def fit(self, *args, **kwargs) :
        return self._fit(*args, **kwargs)
    
    def transform(self, *args, **kwargs) :
        return self._transform(*args, **kwargs)

    def save(self, path, format='pickle') :
        return self._save(path, format)

    def load(self, path, format='pickle') :
        return self._load(path, format)

class WOEBase(ModelBase) :

    def __init__(self, data, xcols=..., ycols=..., bins=10, *args, **kwargs):
        super().__init__(data, xcols, ycols, *args, **kwargs)
        self.bins = bins
        self._bin_map = dict()

    def _Interval_to_Tuple(self, intv) :
        return (intv.left, intv.right)

class WOETransform(WOEBase) :
    '''
    Binning on the value by equal-freq method and calculate woe value. The binning intervals are fitted.
    '''
    def __init__(self, data, xcols=..., ycols=..., *args, **kwargs):
        super().__init__(data, xcols, ycols, *args, **kwargs)

    def _get_kwargs(self, **kwargs) :
        
        bins = kwargs.get('bins', self.bins)
        data = kwargs.get('data', self.data)
        xcols = kwargs.get('xcols', self.xcols)
        ycols = kwargs.get('ycols', self.ycols)

        return data, xcols, ycols, bins
    

    def _fit(self, *args, **kwargs) :
        '''
        cut the original value and build the mapping dict.
        '''
        data, xcols, ycols, bins = self._get_kwargs(**kwargs)
        
        for i, col in enumerate(xcols) :
            n_uniq_val = data[col].nunique()
            if n_uniq_val < bins :
                print(f'Skipped. {col} has less unique value than expected bins:{bins}.')
                continue

            x = data[col].values
            y = data[ycols].values.flatten()

            # Initial binning by any simple method. 
            # It is possible to split the data into small bins becase they are to be merged in next steps
            xbins = pd.qcut(x, bins, duplicates='drop')

            woe_df = get_woe_df(x, y, xbins).reset_index()
            xbins = dict(zip(woe_df['xbins'].tolist(), woe_df['woe'].tolist()))
            
            # Save the interval-to-woe mapping for future tranform use
            self._bin_map[col] = {
                'xbins': xbins,
            }

            print(f"{'.'*i}", end='\r')
    
    def _transform(self, *args, **kwargs) :
        '''
        use the fitted mapping dict to transform the variable value into woe values. 
        '''
        if len(self._bin_map) < 1 :
            raise ValueError("woe bin map hasn't beend fitted.")
        
        data, xcols, ycols, bins = self._get_kwargs(**kwargs)
        
        res_df = data[xcols].copy()

        def inbins(x, bin_map) :
            for k in bin_map.keys() :
                if x in k :
                    return k, bin_map[k]
            return -1, 0
        
        for i, col in enumerate(xcols) :
            n_uniq_val = data[col].nunique()
            if n_uniq_val < bins :
                print(f'Skipped. {col} has less unique value than expected bins:{bins}.')
                continue

            x = data[col]

            xbins = self._bin_map[col]['xbins']
            xbin1 = x.map(lambda x: inbins(x, xbins)[0]) # [0] means the bins
            xwoe1 = x.map(lambda x: inbins(x, xbins)[1]) # [1] means the value
            
            res_df[col+'_bin'] = xbin1
            res_df[col+'_woe'] = xwoe1
            print(f"{'.'*i}", end='\r')

        self.result = res_df
        return res_df 
        
    def _save(self, path, format) :
        if format == 'pickle' :
            with open(path, 'wb') as fp :
                pickle.dump(self._bin_map, fp)
        elif format == 'json' :
            output = dict()
            for key, val in self._bin_map.items() :
                xbins = []
                for i, k in enumerate(val['xbins'].keys()) :
                    if isinstance(k, pd.Interval) :
                        k1, k2 = self._Interval_to_Tuple(k)
                        xbins.append({
                            'left' : k1, 
                            'right' : k2,
                            'closed' : k.closed,
                            'value' : val['xbins'][k],
                        })
                output[key] = xbins
            with open(path, 'w', encoding='utf8') as fp :
                json.dump(output, fp)
        else :
            IOError("format not supported yet.")
            
    def _load(self, path, format) :
        if format == 'pickle' :
            with open(path, 'rb') as fp :
                self._bin_map = pickle.load(fp)

            a = {"a":1, "b":2}
            a.items()
        elif format == 'json' :
            with open(path, 'r', encoding='utf8') as fp :
                loaded = json.load(fp)
            bin_map = dict()
            for key, val in loaded.items() :
                xbins = dict()
                for v in val :
                    xbins[pd.Interval(v['left'], v['right'], v['closed'])] = v['value']
                
                bin_map[key] = {'xbins': xbins}

            self._bin_map = bin_map

        else :
            IOError("format not supported yet.")


class MonotonicWOETransform(WOEBase) :
    '''
    Re-order the value bins so to let the bins have monotonic metric value.
    Eg, the woe value increase along the bins increase.   
    '''
    def __init__(self, data, xcols=..., ycols=..., init_bins=20, *args, **kwargs):
        self.init_bins = init_bins
        super().__init__(data, xcols, ycols, *args, **kwargs)

    def _get_kwargs(self, **kwargs) :
        
        init_bins = kwargs.get('init_bins', self.init_bins)
        bins = kwargs.get('bins', self.bins)
        data = kwargs.get('data', self.data)
        xcols = kwargs.get('xcols', self.xcols)
        ycols = kwargs.get('ycols', self.ycols)

        return data, xcols, ycols, init_bins, bins
    
    def _fit(self, *args, **kwargs) :
        '''
        cut the original value and build the mapping dict.
        '''
        data, xcols, ycols, init_bins, bins = self._get_kwargs(**kwargs)
        
        for i, col in enumerate(xcols) :
            n_uniq_val = data[col].nunique()
            if n_uniq_val < bins :
                print(f'Skipped. {col} has less unique value than expected bins:{bins}.')
                continue

            x = data[col].values
            y = data[ycols].values.flatten()

            # Initial binning by any simple method. 
            # It is possible to split the data into small bins becase they are to be merged in next steps
            xbins = pd.qcut(x, init_bins, duplicates='drop')
            df = pd.DataFrame.from_dict({'x': x, 'y': y, 'xbins': xbins}, orient='columns')

            woe_df = get_woe_df(x, y, xbins).reset_index()
            xbins = dict(zip(woe_df['xbins'].tolist(), woe_df['woe'].tolist()))
            
            woe_df['woe_bin'] = pd.qcut(woe_df['woe'], bins, duplicates='drop')
            woe_df = df[['x', 'xbins']].merge(woe_df, on='xbins', how='left')
            
            woe_bin = get_woe_df(x, y, woe_df['woe_bin']).reset_index()
            wbins = dict(zip(woe_bin['xbins'].tolist(), woe_bin['woe'].tolist()))

            # Save the interval-to-woe mapping for future tranform use
            self._bin_map[col] = {
                'xbins': xbins,
                'wbins': wbins,
            }

            print(f"{'.'*i}", end='\r')
    
    def _transform(self, *args, **kwargs) :
        '''
        use the fitted mapping dict to transform the variable value into woe values. 
        '''
        if len(self._bin_map) < 1 :
            raise ValueError("woe bin map hasn't beend fitted.")
        
        data, xcols, ycols, init_bins, bins = self._get_kwargs(**kwargs)
        
        res_df = data[xcols].copy()

        def inbins(x, bin_map) :
            for k in bin_map.keys() :
                if x in k :
                    return k, bin_map[k]
            return -1, 0
        
        for i, col in enumerate(xcols) :
            n_uniq_val = data[col].nunique()
            if n_uniq_val < bins :
                print(f'Skipped. {col} has less unique value than expected bins:{bins}.')
                continue

            x = data[col]

            xbins = self._bin_map[col]['xbins']
            wbins = self._bin_map[col]['wbins']
            xwoe1 = x.map(lambda x: inbins(x, xbins)[1]) # [1] means the value
            xbin2 = xwoe1.map(lambda x: inbins(x, wbins)[0]) # [0] means the bins
            xwoe2 = xwoe1.map(lambda x: inbins(x, wbins)[1]) # [1] means the value
            
            res_df[col+'_bin'] = xbin2
            res_df[col+'_woe'] = xwoe2
            print(f"{'.'*i}", end='\r')

        self.result = res_df
        return res_df 
        
    def _save(self, path, format) :
        if format == 'pickle' :
            with open(path, 'wb') as fp :
                pickle.dump(self._bin_map, fp)
        elif format == 'json' :
            output = dict()
            for key, val in self._bin_map.items() :
                xbins = []
                for i, k in enumerate(val['xbins'].keys()) :
                    if isinstance(k, pd.Interval) :
                        k1, k2 = self._Interval_to_Tuple(k)
                        xbins.append({
                            'left' : k1, 
                            'right' : k2,
                            'closed' : k.closed,
                            'value' : val['xbins'][k],
                        })
                wbins = []
                for i, k in enumerate(val['wbins'].keys()) :
                    if isinstance(k, pd.Interval) :
                        k1, k2 = self._Interval_to_Tuple(k)
                        wbins.append({
                            'left' : k1, 
                            'right' : k2,
                            'closed' : k.closed,
                            'value' : val['wbins'][k],
                        })

                output[key] = { 'xbins' : xbins, 'wbins' : wbins }

            with open(path, 'w', encoding='utf8') as fp :
                json.dump(output, fp)
        else :
            IOError("format not supported yet.")
            
    def _load(self, path, format) :
        if format == 'pickle' :
            with open(path, 'rb') as fp :
                self._bin_map = pickle.load(fp)

            a = {"a":1, "b":2}
            a.items()
        elif format == 'json' :
            with open(path, 'r', encoding='utf8') as fp :
                loaded = json.load(fp)
            bin_map = dict()
            for key, val in loaded.items() :
                xbins = dict()
                for v in val['xbins'] :
                    xbins[pd.Interval(v['left'], v['right'], v['closed'])] = v['value']
                
                wbins = dict()
                for v in val['wbins'] :
                    wbins[pd.Interval(v['left'], v['right'], v['closed'])] = v['value']
                
                bin_map[key] = {'xbins': xbins, 'wbins': wbins}

            self._bin_map = bin_map

        else :
            IOError("format not supported yet.")
if __name__ == '__main__' :
    
    df = pd.read_csv('E:/workspace/feature-eval/data/investing_program_prediction_data.csv')
    
    from preprocess import categories_to_integer, zscore_normalize, detect_variable_type, weight_of_evidence

    ycols = ['InvType']
    xcols = [ col for col in df.columns if col not in ycols]
    ccols, ncols = detect_variable_type(df, xcols)

    # convert categorical y into integer-based y
    df[ycols] = df[ycols].apply(categories_to_integer, axis=0)
    
    # preprocess x
    df[ccols] = df[ccols].apply(categories_to_integer,axis=0)
    df[ncols] = df[ncols].apply(zscore_normalize, axis=0)
    # df[ncols] = df[ncols].apply(lambda x: weight_of_evidence(x, df[ycols].values.flatten()), axis=0)
    
    woebin = MonotonicWOETransform(df, xcols, ycols, 10) 
    woebin.fit()

    woebin.save('woebin.b')
    woebin.save('woebin.json', format='json')

    woebin.load('woebin.b')
    woebin.load('woebin.json', format='json')

    result = woebin.transform(data=df.head(1000), xcols=xcols)

    result.to_csv('woebin.csv', index=None)

    woetrn = WOETransform(df, xcols, ycols, 15) 
    woetrn.fit()

    woetrn.save('woe.b')
    woetrn.save('woe.json', format='json')

    woetrn.load('woe.b')
    woetrn.load('woe.json', format='json')

    result = woetrn.transform(data=df.head(1000), xcols=xcols)

    result.to_csv('woe.csv', index=None)

    print(result)


    
