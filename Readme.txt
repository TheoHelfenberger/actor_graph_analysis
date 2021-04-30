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
