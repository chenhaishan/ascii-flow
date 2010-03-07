def preprocess(options, data):
    # replace all tabs with spaces
    data = data.replace('\t', options.tabstop * ' ')
    # convert into array of text lines
    return data.split('\n')


