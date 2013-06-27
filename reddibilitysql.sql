CREATE USER 'reddibility'@'localhost' IDENTIFIED BY 'PASSWORD' ;
SET PASSWORD FOR 'reddibility'@'localhost' = PASSWORD('awsmysql');
CREATE Database redditdata.sql;
GRANT ALL  ON *.* TO 'reddibility'@'localhost'