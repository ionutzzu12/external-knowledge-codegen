# get digits only from a string var_0 using lambda function
''.join([x for x in var_0 if x.isdigit()])
''.join(filter(lambda c: c.isdigit(), var_0))

# count the occurrences of items in list var_0
[[x, var_0.count(x)] for x in set(var_0)]
dict((x, var_0.count(x)) for x in set(var_0))


