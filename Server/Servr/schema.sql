DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE Table params (
	temperature FLOAT, 
	rh INTEGER, 
	co2 INTEGER
);
	
CREATE Table envdata (
	datetime TEXT, 
	temperature FLOAT, 
	rh Float, 
	co2 Float, 
	o2 Float, 
	airspeed Float, 
	temp_relay BOOL, 
	rh_relay BOOL, 
	co2_relay BOOL
);

CREATE Table currentstates (
	datetime TEXT, 
	temperature FLOAT, 
	rh Float, 
	co2 Float, 
	o2 Float, 
	airspeed Float, 
	temp_relay BOOL, 
	rh_relay BOOL, 
	co2_relay BOOL);
