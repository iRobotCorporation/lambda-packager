import subprocess
import pkg_resources
import sys
import argparse

def run_make(action, bucket=None, bucket_prefix=None, make_args=[]):
    with pkg_resources.resource_stream(__name__, 'Makefile') as fp:
        args = ['make', '-f', '-']
        if bucket:
            args.append('BUCKET={}'.format(bucket))
        if bucket_prefix:
            args.append('BUCKET_PREFIX={}'.format(bucket_prefix))
        args.append(action)
        args.extend(make_args)
        return subprocess.call(args, stdin=fp)

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('action', choices=['config_from_template', 'build', 'upload', 'clean'])
    parser.add_argument('--bucket')
    parser.add_argument('--bucket_prefix')
    
    args, other_args = parser.parse_known_args()
    
    sys.exit(run_make(args.action,
                      bucket=args.bucket,
                      bucket_prefix=args.bucket_prefix,
                      make_args=other_args))

if __name__ == '__main__':
    main()