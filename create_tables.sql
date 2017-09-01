USE host;

DROP TABLE IF EXISTS `urls`;
DROP TABLE IF EXISTS `domain_ip`;

CREATE TABLE urls (
  id            INT NOT NULL AUTO_INCREMENT,
  url           VARCHAR(50),
  creation_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

CREATE TABLE domain_ip (
  id      INT NOT NULL AUTO_INCREMENT,
  domain  VARCHAR(100),
  ip      INT UNSIGNED,
  url_id  INT,
  counter INT UNSIGNED DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE (domain, ip, url_id),
  CONSTRAINT FOREIGN KEY `url_fk` (`url_id`) REFERENCES `urls`
  (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

INSERT INTO domain_ip (domain, ip, url_id, counter)
VALUES (%s, INET_ATON( % s), %s, %s)
ON DUPLICATE KEY UPDATE counter = counter + VALUES (counter);


SELECT
  id,
  url
FROM urls
WHERE creation_time = % s AND url IN % s;