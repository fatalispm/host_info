CREATE DATABASE host;

CREATE TABLE urls (
  id                INT       NOT NULL AUTO_INCREMENT,
  url               VARCHAR(50),
  creation_time     TIMESTAMP          DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

CREATE TABLE domain_ip (
  id      INT NOT NULL AUTO_INCREMENT,
  domain  VARCHAR(100),
  ip INT UNSIGNED,
  counter INT UNSIGNED DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE (domain, ip)
);

CREATE TABLE url_domain (
  domain_id INT,
  url_id  INT,
  counter INT DEFAULT 1,
  PRIMARY KEY (`domain_id`, url_id),
  CONSTRAINT FOREIGN KEY `domain_fk` (`domain_id`) REFERENCES `domain_ip`
  (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT FOREIGN KEY `url_fk` (`url_id`) REFERENCES `urls`
  (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

