outdir=./temp/output
mkdir -p $outdir
python3 main_cli.py ./data/input.txt  -o $outdir $1 $2 $3 $4

ls -al $outdir
