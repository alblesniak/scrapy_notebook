docker build -t scrapy_notebook -f Dockerfile .
docker run --env PORT=8888 -t -p 8888:8888 scrapy_notebook