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
	unsubs = request.form.get("unsubs")

	first_name = request.form.get("first_name")
	last_name = request.form.get("last_name")
	license_type = request.form.get("license_type")



	filters=[]
	filters.extend([domain,version,status,platform_version,license,os,multiple,start,end,unsubs])
	realFilters = []
	for item in filters:
		if item == "on":
			string = "multiple accounts" if multiple == "on" else "removed unsubs"
			realFilters.append(string)
		elif item != "" and item != [] and item != None:
			realFilters.append(item)
		else:
			continue


	



	osQuery = ""
	for item in os:
		osQuery = osQuery + "devices.platform = '" + item + "' or "
	osQuery = osQuery[:-4]
	osQuery = "" if osQuery == "" else "(" + osQuery + ") and "
	versionQuery = "" if version == "" else "devices.app_version = '" + version + "' and "
	platform_versionQuery = "" if platform_version == "" else "devices.platform_version = '" + platform_version + "' and "
	devicesQuery = osQuery + versionQuery + platform_versionQuery


	licenseQuery = "" if license == "" else "subscriptions.type = '" + license + "' and "
	statusQuery = "" if status == "" else "subscriptions.status = '" + status + "' and "
	subscriptionsQuery = licenseQuery + statusQuery
	

	query = "SELECT accounts.user_id,accounts.name,accounts.email,GROUP_CONCAT(DISTINCT(subscriptions.type)),accounts.created_at FROM accounts INNER JOIN devices ON accounts.user_id = devices.user_id INNER JOIN subscriptions ON accounts.user_id = subscriptions.user_id WHERE "
	query = query + devicesQuery +  subscriptionsQuery

	

	if domain != "":
		query = query + "accounts.email like '%" + domain + "' and "

	if unsubs == "on":
		query = query + "accounts.email NOT IN(SELECT email from email_unsubscribers) and "

	startQuery = ""
	endQuery = ""
	if start != "":
		start_tuple = dt.datetime.strptime(start, "%B %d, %Y")
		start_epoch = start_tuple.timestamp()
		startQuery = str(start_epoch) + "<"
		query = query + startQuery + "accounts.created_at and "

	if end != "":
		end_tuple = dt.datetime.strptime(end, "%B %d, %Y")
		end_epoch = end_tuple.timestamp()
		endQuery = "<" + str(end_epoch)
		query = query + "accounts.created_at" + endQuery + " and "


	query = query[:-4]

	if query == "SELECT accounts.user_id,accounts.name,accounts.email,GROUP_CONCAT(DISTINCT(subscriptions.type)),accounts.created_at FROM accounts INNER JOIN devices ON accounts.user_id = devices.user_id INNER JOIN subscriptions ON accounts.user_id = subscriptions.user_id WH":
		query = "SELECT accounts.user_id,accounts.name,accounts.email,GROUP_CONCAT(DISTINCT(subscriptions.type)),accounts.created_at FROM accounts INNER JOIN devices ON accounts.user_id = devices.user_id INNER JOIN subscriptions ON accounts.user_id = subscriptions.user_id"
	
	query = query + " GROUP BY accounts.user_id" if multiple != "on" else query + " GROUP BY accounts.user_id having count(DISTINCT(devices.id)) > 1"
	
	print("+++++++++++++++++++")
	print(query)
	print("+++++++++++++++++++")
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute(query)
	data = cursor.fetchall()
	with open('results.csv', 'w') as csvfile:
		fieldnames = ['email']
		if first_name == "on":
			fieldnames.append('first_name')
		if last_name == "on":
			fieldnames.append('last_name')
		if license_type == "on":
			fieldnames.append('license_type')
		writer = csv.writer(csvfile)
		writer.writerow(fieldnames)
		for item in data:
			# print(item[1])
			# query = "SELECT platform from devices where user_id=" + item[1]
			# print(query)
			# cursor.execute(query)
			# os=cursor.fetchall()
			# print(os)
			row = [item[2]]
			if first_name == "on":
				row.append(item[1].split()[0])
			if last_name == "on":
				row.append(item[1].split()[-1])
			if license_type == "on":
				row.append(item[3])
			writer.writerow(row)

	return render_template("filter.html",data=data,domain=domain,filters=realFilters)
	# try:
	# 	return send_file('results.csv', attachment_filename='results.csv')
	# except Exception as e:
	# 	return str(e)


if __name__ == "__main__":
  app.run(debug=True)