# Start neo4j docker 

docker run \
    --name moviesdb \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $PWD/neo4j/import:/var/lib/neo4j/import \
    --env NEO4J_AUTH=neo4j/test \
    neo4j:latest



bin/neo4j-admin import --database=moviesdb \
--nodes=/var/lib/neo4j/import/actors_file.csv \
--nodes=/var/lib/neo4j/import/movies_file.csv \
--relationships=/var/lib/neo4j/import/acted_in_file.csv

.\bin\neo4j-admin.bat import --database=anothertest --nodes=import\actors_file.csv --nodes=import\movies_file.csv --relationships=import\acted_in_file.csv




bin/neo4j-admin import --database=neo4j \
--nodes=/var/lib/neo4j/import/actors_file.csv \
--nodes=/var/lib/neo4j/import/movies_file.csv \
--relationships=/var/lib/neo4j/import/acted_in_file.csv


docker run \
    --name moviesdb \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $PWD/neo4j/import:/var/lib/neo4j/import \
    --env NEO4J_AUTH=neo4j/test \
    neo4j:latest \
    bin/neo4j-admin import --database=neo4j \
    --nodes=/var/lib/neo4j/import/actors_file.csv \
    --nodes=/var/lib/neo4j/import/movies_file.csv \
    --relationships=/var/lib/neo4j/import/acted_in_file.csv



docker run \
    -rm \
    -p7474:7474 -p7687:7687 \
    --volumes-from moviesdb \
    --env NEO4J_AUTH=neo4j/test \
    --env 'NEO4JLABS_PLUGINS=["apoc", "graph-data-science"]' \
    neo4j:latest


Match (m:Movie)--(a:Actor)--(m2:Movie) where m.primaryTitle starts with 'Captain' return m,a,m2

eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRoZW8uaGVsZmVuYmVyZ2VyQGRvY2Rvay5oZWFsdGgiLCJtaXhwYW5lbElkIjoiZ29vZ2xlLW9hdXRoMnwxMTczNjMwMjY0MTg1NzcyMjM1MDciLCJtaXhwYW5lbFByb2plY3RJZCI6IjRiZmIyNDE0YWI5NzNjNzQxYjZmMDY3YmYwNmQ1NTc1Iiwib3JnIjoiRG9jZG9rLmhlYWx0aCIsInB1YiI6Im5lbzRqLmNvbSIsInJlZyI6IlRoZW8gSGVsZmVuYmVyZ2VyIiwic3ViIjoibmVvNGotZGVza3RvcCIsImV4cCI6MTY1MTIzMDc5NCwidmVyIjoiKiIsImlzcyI6Im5lbzRqLmNvbSIsIm5iZiI6MTYxOTY5NDc5NCwiaWF0IjoxNjE5Njk0Nzk0LCJqdGkiOiJRSVNYWlV6d0oifQ.yQXOVRnMVVrFWjGUHgheZQjtx8ydhX47vuxcg1SfAOijNv9ag8bMlZAsRYpQdz8fdbqUV37K6f9581RXOt69nzbTrnQ257mSP9NxNI5374u6-nDpqcqYJCwY0HAVWgFfg_-sa11OOwwfCbBblieYN7GZx20R1YbVI6A30pifdbmFFMzqq1mlMuuWULJjF7qRTxONsdGNOvnBq5TsccueA1b6PD_yoVcP337FdrBfU1Ab6dOOxeuUTW9TO-gLHuJ6-fZ21Npo9QMOLGZ_m0by5LNTGe_6e3rcbGkvBt-HP3GHt9CqXCAihsg4IJNEce_-TArdQ12slug_bYyKusPGoQ



eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Ii4rQC4rIiwibWl4cGFuZWxJZCI6IjE3OTFkYjJiMDE3ZDViLTA2Yjg4YTQ1N2VhYmMyOC03ZTIyNjc1Yy01MTAwMDAtMTc5MWRiMmIwMTg4N2UiLCJtaXhwYW5lbFByb2plY3RJZCI6IjRiZmIyNDE0YWI5NzNjNzQxYjZmMDY3YmYwNmQ1NTc1Iiwib3JnIjoiLioiLCJwdWIiOiJuZW80ai5jb20iLCJyZWciOiIgIiwic3ViIjoibmVvNGotZGVza3RvcCIsImV4cCI6MTY1MTIzNjk3NSwidmVyIjoiKiIsImlzcyI6Im5lbzRqLmNvbSIsIm5iZiI6MTYxOTcwMDk3NSwiaWF0IjoxNjE5NzAwOTc1LCJqdGkiOiJGeTBvczEwSXAifQ.02k2MdqL6p_f-Xm4zfORWjuLA1cLwpx8Ia9YuEavPexW3evD4HG8V5-K3ySYBT_dilM9AFGpRVRRvGcxtJVuY0IUVhv5FOV53YusdNFonHL2sJVlI8ArZp1SrsP7nxjbTpWMn6l3rLD9ClYPMav8vQVEirpKZ4LksL7fqniE0dpc1LwxOSbAF-ruDy3sDsuJRnhdETFhvrGAYFdqP7NVaOTwbCfFCMr502F-tmdUYu24PS2PCSOLTdKZRjYdy6HWDTEAgXhinQyJIga5AbdGP7sxJax_Fw-bzGGxgRO_wLizkdTj2isEbWBqPO05jZWl4tJVUfBGqmZHuLgLJd2h5Q