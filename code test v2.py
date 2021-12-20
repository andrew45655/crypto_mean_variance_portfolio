# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 20:51:53 2021

@author: Andrew
"""

import pandas as pd
import numpy as np
import requests
import datetime  as dt
import matplotlib.pyplot as plt
import json
import time
import hmac
from requests import Request



class PortfolioEngine:
    
    def __init__(self,coins,start_time,end_time,number_portfolios,risk_free_rate,B_days ):
        self.init_time=dt.datetime(1970,1,1)
        self.coins=coins
        self.start_time=int((start_time-self.init_time).total_seconds())
        self.end_time=int((end_time-self.init_time).total_seconds())
        self.number_portfolios=number_portfolios
        self.risk_free_rate=risk_free_rate
        self.B_days=B_days
    
    def get_request(self):
        ts = int(time.time() * 1000)
        request = Request('GET', 'https://ftx.com/api')
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        signature = hmac.new('spfdCEVRV0xXYIBwLrkyGLgBdasuM8CEShVwehsN'.encode(), signature_payload, 'sha256').hexdigest()
        
        request.headers['FTX-KEY'] = 'eGRxxhmVpv1fOAFzntT43uVhW_5xI3hsWwQ56uAJ'
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)
        


    def draw_data(self,coins,start_time,end_time):
        head="https://ftx.com/api"
        coins_df={}
        for coin in coins:
            url=head+"/markets/{coin}/candles?resolution=3600&start_time={start_time}&end_time={end_time}".format(coin=coin,start_time=start_time,end_time=end_time)
            res=requests.get(url)
            if res.status_code==200:
                print('Sucess to draw %s data!'%coin)
                res=res.json()
                markets=pd.DataFrame(res['result'])
                coins_df[coin]=markets[['startTime','close']]
        
            elif res.status_code==404:
                print("Not Found for url: %s"%url)
                return None
        return coins_df    
        
        
    def parse_df(self,coins_df,coins):
        df=pd.DataFrame(coins_df[self.coins[0]]['startTime'])
        
        for coin in self.coins:
            temp_df=pd.DataFrame(coins_df[coin][['startTime','close']])
            temp_df.columns=['startTime',coin]
            df=df.merge(temp_df,how="left",on="startTime")
        return df.set_index('startTime')
        
    
    def calculate_weights(self,df,number_portfolios,risk_free_rate,B_days):
        results = np.zeros((3,number_portfolios))
        weights_records=[]
        returns = df.pct_change() 
        mean_returns = returns.mean() 
        cov_matrix = returns.cov() 
        for i in range(number_portfolios):
            weights = np.random.random(len(df.columns))  # randomize weighting
            weights /= np.sum(weights)
            weights_records.append(weights)
            portfolio_standard_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(B_days)  
            portfolio_return = np.sum(mean_returns * weights) * (B_days)
            results[0, i] = portfolio_standard_dev
            results[1, i] = portfolio_return
            results[2, i] = (portfolio_return - risk_free_rate) / portfolio_standard_dev 
    
        weights = weights_records
        return weights,results
    
    
    
    def allocation_to_dict(self,df,weights,port_idx):
        allocation={}
        for idx,coin in enumerate(df.columns):
            allocation['perp_contract_%s'%coin.replace("-PERP","")]= round(weights[port_idx][idx] * 100, 2)
        return allocation
    
    def calculate_max_sharpeRatio_portfolio(self,results,df,weights):
        max_sharpeRatio_index = np.argmax(results[2]) #find the max sharpe ratio index
        sd_sharpe, rt_sharpe = results[0, max_sharpeRatio_index], results[1, max_sharpeRatio_index] 
        allocation=self.allocation_to_dict(df,weights,max_sharpeRatio_index)
        return sd_sharpe,rt_sharpe,allocation
    
    def calculate_min_vol_portfolio(self,results,df,weights):
        min_vol_idx = np.argmin(results[0]) # find the min vol index
        sd_min, rt_min = results[0, min_vol_idx], results[1, min_vol_idx] 
        allocation=self.allocation_to_dict(df,weights,min_vol_idx)
        return sd_min,rt_min,allocation
    
    
    def draw_efficent_frontier(self,rt_sharpe,sd_sharpe,max_sharpe_allocation,rt_min,sd_min,min_vol_allocation,results):
        print("Maximum Sharpe Ratio Portfolio Allocation\n")
        print("Annualised Return:", round(rt_sharpe, 2))
        print("Annualised Volatility:", round(sd_sharpe, 2))
        print("\n")
        print(max_sharpe_allocation)
        print("-" * 50)
        print("Minimum Volatility Portfolio Allocation\n")
        print("Annualised Return:", round(rt_min, 2))
        print("Annualised Volatility:", round(sd_min, 2))
        print("\n")
        print(min_vol_allocation)
        print("-" * 50)
        print("\n")
        plt.figure(figsize=(10, 7))
        plt.scatter(results[0, :], results[1, :], c=results[2, :], cmap='YlGnBu', marker='o', s=10, alpha=0.3)
        plt.colorbar()
        plt.scatter(sd_sharpe, rt_sharpe, marker='*', color='c', s=500, label='Maximum Sharpe ratio') 
        plt.scatter(sd_min, rt_min, marker='*', color='crimson', s=500, label='Minimum volatility')
        plt.title('Simulated Portfolio Optimization based on Efficient Frontier')
        plt.xlabel('annualised volatility')
        plt.ylabel('annualised returns')
        plt.legend(labelspacing=0.8)
        plt.show()
    
    
    def output_file(self,max_sharpe_allocation,min_vol_allocation):
        with open('max_sharpRatio_weighting.txt','w') as file:
            file.write(json.dumps(max_sharpe_allocation))
        with open('min_vol_weighting.txt','w') as file:
            file.write(json.dumps(min_vol_allocation))  
    
    
    def main(self):
        self.get_request()
        coins_df=self.draw_data(coins,self.start_time,self.end_time)
        if coins_df:
            df=self.parse_df(coins_df,self.coins)
            weights,results=self.calculate_weights(df,self.number_portfolios,self.risk_free_rate,self.B_days)
            sd_sharpe,rt_sharpe,max_sharpe_allocation=self.calculate_max_sharpeRatio_portfolio(results,df,weights)
            sd_min,rt_min,min_vol_allocation=self.calculate_min_vol_portfolio(results,df,weights)
            self.output_file(max_sharpe_allocation,min_vol_allocation)
            self.draw_efficent_frontier(rt_sharpe,sd_sharpe,max_sharpe_allocation,rt_min,sd_min,min_vol_allocation,results)
    
if __name__=="__main__":
    coins=['BTC-PERP','ETH-PERP','ADA-PERP']
    start_time=dt.datetime(2021,10,1,0,0,0)
    end_time=dt.datetime(2021,10,31,23,0,0)
    number_portfolios = 2500 # number of portfolio simulations
    risk_free_rate = 0.0178 
    B_days=365*24 #
    porfolioEngine=PortfolioEngine(coins, start_time, end_time, number_portfolios, risk_free_rate, B_days)
    porfolioEngine.main()


