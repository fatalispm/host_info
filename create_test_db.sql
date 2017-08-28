CREATE DATABASE test_host;

CREATE USER 'test'@'localhost' IDENTIFIED BY 'test';

GRANT ALL ON test_host.* TO 'test'@'localhost';

USE test_host;

CREATE TABLE urls (
  id                INT       NOT NULL AUTO_INCREMENT,
  url               VARCHAR(50),
  creation_time     TIMESTAMP          DEFAULT CURRENT_TIMESTAMP,
  modification_time TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
  ,
  PRIMARY KEY (`id`),
  UNIQUE (`url`)
);

CREATE TABLE link_info (
  id      INT NOT NULL AUTO_INCREMENT,
  link    VARCHAR(255),
  domain  VARCHAR(100),
  counter INT          DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE (`link`)
);

CREATE TABLE ip_info (
  id      INT NOT NULL AUTO_INCREMENT,
  ip      VARCHAR(255),
  counter INT          DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE (`ip`)
);

CREATE TABLE link_ips (
  id INT NOT NULL AUTO_INCREMENT,
  link_id INT,
  ip_id   INT,
  url_id  INT,
  PRIMARY KEY (`id`),
  CONSTRAINT FOREIGN KEY `link_fk` (`link_id`) REFERENCES `link_info`
  (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT FOREIGN KEY `ip_fk` (`ip_id`) REFERENCES `ip_info`
  (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT FOREIGN KEY `url_fk` (`url_id`) REFERENCES `urls`
  (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

