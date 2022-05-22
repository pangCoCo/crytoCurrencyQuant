import utils.QuantLogging

def testQuantLogging() :
    log = utils.QuantLogging.Log('test1')
    log.info('我是test1')
    log2 = utils.QuantLogging.Log('test2')
    log2.info('我是test2')
    log.info('我还是test1')

if __name__ == '__main__':
    testQuantLogging()