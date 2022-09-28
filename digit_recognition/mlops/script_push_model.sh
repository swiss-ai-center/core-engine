input="./numbers.dat"

while IFS= read -r line; do num=$line; done < $input

numbers=$(python3 -c "n='$num';new=n.replace(',','_');print(new)")
name="mnist_model"
src="./src/models/$name.h5"
dst="$2/${name}_${numbers}"

echo "Push dataset $dst on S3"

S3_URL=$1 S3_KEY_ID=$3 S3_SECRET_KEY=$4 python3 ./src/s3client.py push $src $dst
