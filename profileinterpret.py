
'''
profiler output:

{key:val}

key = filename, line #, function name
val = number of calls, somthing, totaltime, cumulative time

'''
import marshal

stats = marshal.load(open('profileresults.txt'))

keys = stats.keys()
keys.sort()

calls = [k+stats[k][:4] for k in keys]

i=0
while calls[i][0].startswith('/usr/lib'):i+=1

calls = calls[i:]
calls.sort((lambda b,a:cmp(a[-2],b[-2])))

print 'Filename\t\tLine #\tFunction Name\t\t# calls\traw calls\ttotime\tctime'
for call in calls[:100]:
    print "%s\t\t%s\t%s\t\t%s\t%s\t%s\t%s"%call
