CREATE TABLE tgm_user(
	id INT,
	first_name VARCHAR(30),
	username VARCHAR(30),
	PRIMARY KEY (id)
);

CREATE TABLE task_type(
	id INT,
	name VARCHAR(30) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE task(
	id INT,
	name VARCHAR(30) NOT NULL,
	task_type_id INT,
	PRIMARY KEY (id),
	FOREIGN KEY (task_type_id) REFERENCES task_type(id)
);

CREATE TABLE task_log(
	id INT AUTO_INCREMENT,
	task_start DATETIME NOT NULL,
	task_end DATETIME,
	user_id INT,
	task_id INT,
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES tgm_user(id),
	FOREIGN KEY (task_id) REFERENCES task(id)
);