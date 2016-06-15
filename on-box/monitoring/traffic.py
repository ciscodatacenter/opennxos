"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Monitoring
:Box Type:On-Box
:Title:Traffic Monitoring
:Short Description:This script is to monitor interfaces throughput.
:Long Description:This script is to monitor interfaces with non-zero bps
this includes bps out, bps in, and converts txload/rxload to a percentage.
:Input:command to check the interface counters
     e.g show interface
:Output:Details of utlization for all interfaces.
"""
from cli import *
import json

#Issue the command "show interface". Returns a dictionary.
intfinfo = json.loads(clid("show interface"))

#Create output format template.
template = "{0:15} {1:65} {2:10} {3:20} {4:10} {5:10} {6:20} {7:10}"

#Create interface list object.
intfinfo_list = intfinfo['TABLE_interface']['ROW_interface']

def eth_interface_parser(interface):
	"""
	Parses an interface's dictionary and returns the following output
	if traffic is detected on the interface:
	Port, Name, In Mbps, % In (rx load), Kpps, Out Mbps, % Out (tx load), Kpps

	Uses bps_converter function to convert bps to Mbps.
	Uses percentage function to convert load in the form of X/255 to a percent.
	"""
	output = ""
	mbps_in = bps_converter(interface["eth_inrate1_bits"])
	mbps_out = bps_converter(interface["eth_outrate1_bits"])
	rx_load = percentage(interface["eth_rxload"])
	tx_load = percentage(interface["eth_txload"])
	if int(interface["eth_inrate1_bits"]) or int(interface["eth_outrate1_bits"]) > 0:
		if interface["eth_hw_desc"] == "1000/10000 Ethernet" and interface['state'] == 'up':
			output = template.format(interface["interface"], interface["desc"], mbps_in, rx_load, interface["eth_inrate1_pkts"], \
				mbps_out, tx_load, interface["eth_outrate1_pkts"])
	else:
		return False
	return output

def bps_converter(bps):
	"""
	Converts bps to Mbps. Using the formula:
	Megabits per second = bits per second / 1000000
	"""
	mbps = int(bps) / float(1000000)
	return str(mbps)

def percentage(load):
	"""
	Converts interface load to a percentage. Using the formula:
	Load Percentage = 100 * 1 / 255
	"""
	percent_load = 100 * int(load) / float(255)
	return str(percent_load) + '%'

#Print statements. Self explanatory.
print "\n"
print "TRAFFIC (all interfaces with non-zero bps): \n"
print template.format("Port", "Name", "In Mbps", "% In", "Kpps", "Out Mbps", "% Out", "Kpps")
#For loop to iterate through interface list. Using try/except for error handling. Some interfaces don't have the keys we're interested in
#and will raise a key value error. Each interface is passed to eth_interface_parser if it has the matching keys. If it doesn't it is returned as False
#and not printed. This will return only physical interfaces and not the management interface.
for i in intfinfo['TABLE_interface']['ROW_interface']:
	try:
		data = eth_interface_parser(i)
	except:
		data = False
	if data != False:
		print data
