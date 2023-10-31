import sys
from core.processor import Processor


if __name__ == '__main__':
     if len(sys.argv) < 2:
          print('You need to provide at least the target mesh...')
          sys.exit()

     targetMesh = f'{sys.argv[1]}'
     baseMesh = ''
     if len(sys.argv) > 2:
          baseMesh = f'{sys.argv[2]}'

     processor = Processor(targetMesh, baseMesh)
     processor.align()
     