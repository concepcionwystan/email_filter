from flaskext.mysql import MySQL
from flask import Flask, request, render_template,send_file
import datetime as dt
import csv



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

@app.route('/download/')
def download():
	try:
		return send_file('results.csv', attachment_filename='results.csv',as_attachment = True)
	except Exception as e:
		return str(e)

@app.route("/filter",methods=["POST"])
def search():

	domain = request.form.get("domain")
	version = request.form.get("version")
	status = request.form.get("status")
	platform_version = request.form.get("platform_version")
	license = request.form.get("license")
	os = request.form.getlist("os")
	multiple = request.form.get("multiple")
	start = request.form.get("start")
	end = request.form.get("end")

	filters=[]
	filters.extend([domain,version,status,platform_version,license,os,multiple,start,end])

	



	osQuery = ""
	for item in os:
		osQuery = osQuery + "platform = '" + item + "' or "
	osQuery = osQuery[:-4]
	osQuery = "" if osQuery == "" else "(" + osQuery + ") and"
	versionQuery = "" if version == "" else " app_version = '" + version + "' and"
	platform_versionQuery = "" if platform_version == "" else " platform_version = '" + platform_version + "' and"
	devicesQuery = "SELECT user_id from devices WHERE " + osQuery + versionQuery + platform_versionQuery if (osQuery != "" or versionQuery !="" or platform_versionQuery != "") else ""
	devicesQuery = devicesQuery[:-4]




	if license == "" and status == "":
		subscriptionsQuery = ""
	else:
		licenseQuery = "" if license == "" else " type = '" + license + "' and"
		statusQuery = "" if status == "" else " status = '" + status + "' and"
		subscriptionsQuery = "SELECT user_id from subscriptions WHERE" + licenseQuery + statusQuery
		subscriptionsQuery = subscriptionsQuery[:-4]
	
	if multiple == "on":
		subscriptionsQuery = subscriptionsQuery + " group by user_id having count(user_id) > 1"

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


	if query == "SELECT email,user_id,subscription_id,name,created_at from accounts WHERE ":
		query = "SELECT email,user_id,subscription_id,name,created_at from accounts"
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(query)
		data = cursor.fetchmany(5000)
		with open('results.csv', 'w') as csvfile:
			fieldnames = ['email', 'user_id', 'subscription_id','name','created_at']
			writer = csv.writer(csvfile)
			writer.writerow(fieldnames)
			for item in data:
				writer.writerow(item)
	else:
		query = query[:-4]
		print(query)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(query)
		data = cursor.fetchall()
		with open('results.csv', 'w') as csvfile:
			fieldnames = ['email', 'user_id', 'subscription_id','name','created_at']
			writer = csv.writer(csvfile)
			writer.writerow(fieldnames)
			for item in data:
				# print(item[1])
				query = "SELECT platform from devices where user_id=" + item[1]
				# print(query)
				cursor.execute(query)
				os=cursor.fetchall()
				# print(os)
				writer.writerow(item)

	return render_template("filter.html",data=data,domain=domain,filters=filters)
	# try:
	# 	return send_file('results.csv', attachment_filename='results.csv')
	# except Exception as e:
	# 	return str(e)


if __name__ == "__main__":
  app.run(debug=True)