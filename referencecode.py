    def get_general_trend(self,stock):
        # this function analyses the general trend
        # it defines the direction and returns a True if defined

        self._L.info('\n\n### GENERAL TREND ANALYSIS (%s) ###' % stock.name)
        timeout = 1

        try:
            while True:
                self.load_historical_data(stock,interval=gvars.fetchItval['big'])

                # calculate the EMAs
                ema9 = ti.ema(stock.df.close.dropna().to_numpy(), 9)
                ema26 = ti.ema(stock.df.close.dropna().to_numpy(), 26)
                ema50 = ti.ema(stock.df.close.dropna().to_numpy(), 50)

                self._L.info('[GT %s] Current: EMA9: %.3f // EMA26: %.3f // EMA50: %.3f' % (stock.name,ema9[-1],ema26[-1],ema50[-1]))

                # check the buying trend
                if (ema9[-1] > ema26[-1]) and (ema26[-1] > ema50[-1]):
                    self._L.info('OK: Trend going UP')
                    stock.direction = 'buy'
                    return True

                # check the selling trend
                elif (ema9[-1] < ema26[-1]) and (ema26[-1] < ema50[-1]):
                    self._L.info('OK: Trend going DOWN')
                    stock.direction = 'sell'
                    return True

                elif timeout >= gvars.timeouts['GT']:
                    self._L.info('This asset is not interesting (timeout)')
                    return False

                else:
                    self._L.info('Trend not clear, waiting...')

                    timeout += gvars.sleepTimes['GT']
                    time.sleep(gvars.sleepTimes['GT'])

        except Exception as e:
            self._L.info('ERROR_GT: error at general trend')
            self._L.info(e)
            block_thread(self._L,e,self.thName)
