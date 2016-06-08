from subprocess import call
from os import listdir
from os.path import splitext, isdir

format_ = 'png'

for i, fname in enumerate(listdir()):
    root, ext = splitext(fname)    

    if fname.startswith('.'): continue
    if isdir(fname): continue
    if ext != '.dot': continue
    
    print(i, 'render:', fname)
    call([
        'dot',
        '-T' + format_,
        '-o', root + '.' + format_,
        fname,
    ])

print('convert gif file: pathx_axes.gif')
call(['convert', 'pathx_axes.gif', 'pathx_axes.png'])        
