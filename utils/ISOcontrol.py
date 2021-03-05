def ISOc(fname):
    key = fname[:-2]
    if key == "NTC" or fname == "NTC":
        iso = 10
    elif key == "50" or fname == "50":
        iso = 100
    elif key == "100" or fname == "100":
        iso = 200
    elif key == "1K" or fname == "1000" or fname == "1K":
        iso = 400
    elif key == "10K" or fname == "10000" or fname == "10K":
        iso = 600
    elif key == "100K" or fname == "100000" or fname == "100K":
        iso = 800
    else:
        iso = 1600
    return (iso)