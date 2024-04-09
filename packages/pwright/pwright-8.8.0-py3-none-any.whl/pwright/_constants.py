INIT_SCRIPT_HIDE_NAVIGATOR = (
    # https://github.com/microsoft/playwright-python/issues/527#issuecomment-887182658
    # '''
    # navigator.webdriver = false
    # '''
    '''
    Object.defineProperty(navigator, 'webdriver', {get: () => false})
    '''
)
