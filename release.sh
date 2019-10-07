set -ex

USERNAME=jamesleopold
IMAGE=cloudmapper

git pull

# bump version
docker run --rm -v "$PWD":/app jamesleopold/cloudmapper patch
version=`cat VERSION`
echo "version: $version"

# run build
./build.sh

# tag
git add -A
git commit -m "version $version"
git tag -a "$version" -m "version $version"
git push
git push --tags

docker tag $USERNAME/$IMAGE:latest $USERNAME/$IMAGE:$version

# push
docker push $USERNAME/$IMAGE:latest
docker push $USERNAME/$IMAGE:$version
