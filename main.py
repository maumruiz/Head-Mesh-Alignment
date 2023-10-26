import sys
from core.processor import downsampleMesh


if __name__ == '__main__':
     if len(sys.argv) < 3:
          print('You need to provide the base and target meshes...')
          sys.exit()

     targetMesh = f'{sys.argv[1]}'
     baseMesh = f'{sys.argv[2]}'

     downsampleMesh(targetMesh)
     