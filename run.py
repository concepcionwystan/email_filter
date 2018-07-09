from flaskext.mysql import MySQL
from flask import Flask, request, render_template
import datetime as dt



app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'intercom'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'intercomdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route("/")
def hello():
  # conn = mysql.connect()
  # cursor = conn.cursor()

  # cursor.execute("SELECT * from accounts")
  # data = cursor.fetchmany(1000)
  return render_template("index.html")

@app.route("/filter",methods=["GET"])
def search():

	domain = request.args.get("domain")
	version = request.args.get("version")
	status = request.args.get("status")
	platform_version = request.args.get("platform_version")
	license = request.args.get("license")
	os = request.args.getlist("os")
	multiple = request.args.get("multiple")
	start = request.args.get("start")
	end = request.args.get("end")


	



	osQuery = ""
	for item in os:
		osQuery = osQuery + "platform = '" + item + "' or "
	osQuery = osQuery[:-4]
	osQuery = "" if osQuery == "" else "(" + osQuery + ") and"
	versionQuery = "" if version == "" else " app_version = '" + version + "' and"
	platform_versionQuery = "" if platform_version == "" else " platform_version = '" + platform_version + "' and"
	devicesQuery = "SELECT user_id from devices WHERE " + osQuery + versionQuery + platform_versionQuery if (osQuery != "" or versionQuery !="" or platform_versionQuery != "") else ""
	devicesQuery = devicesQuery[:-4]



	# domain = "" if request.args.get("domain") == "" else "and email like '%" + request.args.get("domain") + "'"

	if license == "" and status == "":
		subscriptionsQuery = ""
	else:
		licenseQuery = "" if license == "" else " type = '" + license + "' and"
		statusQuery = "" if status == "" else " status = '" + status + "' and"
		subscriptionsQuery = "SELECT user_id from subscriptions WHERE" + licenseQuery + statusQuery
		subscriptionsQuery = subscriptionsQuery[:-4]
	# license = "" if request.args.get("license") == "" else "type = '" + request.args.get("license") + "'"
	# query = "SELECT user_id,id,type,status from subscriptions WHERE " + license

	query = "SELECT email,user_id,subscription_id,name,created_at from accounts WHERE "
	if devicesQuery != "":
		query = query + "user_id IN(" + devicesQuery + ") and "

	if subscriptionsQuery != "":
		query = query + "user_id IN(" + subscriptionsQuery + ") and "

	if domain != "":
		query = query + "email like '%" + domain + "' and "


	startQuery = ""
	endQuery = ""
	if start != "":
		start_tuple = dt.datetime.strptime(start, "%B %d, %Y")
		start_epoch = start_tuple.timestamp()
		startQuery = str(start_epoch) + "<"
		query = query + startQuery + "created_at and "

	if end != "":
		end_tuple = dt.datetime.strptime(end, "%B %d, %Y")
		end_epoch = end_tuple.timestamp()
		endQuery = "<" + str(end_epoch)
		query = query + "created_at" + endQuery + " and "





	query = query[:-4]

	print(query)

	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute(query)
	data = cursor.fetchall()


	return render_template("filter.html",data=data)

if __name__ == "__main__":
  app.run(debug=True)