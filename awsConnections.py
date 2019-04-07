import numpy as np

"""awsConnections.py: Models aws connections in app stream 2.0 for aws project. 
					Incorporates connection time, streaming time, disconnecting time. 
					Details of a particular connection are stored in seconds in each instance.
					Output is generic aggregate statistics."""

__author__ = "Joaquin Casaubon"

######## Variables ########
# number of hours to run model
hours_model_runs = 1
# number of instances
aws_instances = 4000
# aws cost per hour
aws_one_instance_cost_per_hour = 1.00
# connecting
mean_connection_time = 8 # seconds on average to connect
sigma_connection_time = 2 # seconds of standard deviation
min_connection_time = 5 # seconds minimum for a connection
max_connection_time = 15 # seconds maximum for a connection
# streaming
mean_streaming_time = 300 # seconds on average to stream
sigma_streaming_time = 100 # seconds of standard deviation
min_streaming_time = 20 # seconds minimum for an entire stream session
max_streaming_time = 800 # seconds maximum for an entire stream session
# disconnection, cleanup, back into pool
mean_disconnection_time = 60 # seconds on average to disconnect, cleanup, back in pool
sigma_disconnection_time = 10 # seconds of standard deviation
min_disconnection_time = 5 # seconds minimum for a disconnect, cleanup, back in pool
max_disconnection_time = 70 # seconds maximum for a disconnect, cleanup, back in pool
###########################



######## Global Vars ########
seconds_in_experiment = hours_model_runs * 3600
#############################

# Models behavior of one aws instance
class AwsInstance:
	READY_STATE = 0 # Ready with no connections
	CONNECTED_STATE = 1 # Getting connection
	STREAMING_STATE = 2 # Connected and Streaming
	DISCONNECT_CLEANUP_STATE = 3 # Disconnected placing back into pool

	# initial state of Instance when turned on
	def __init__(self, input_id_num):
		self.id_num = input_id_num
		self.current_state_of_instance = 0
		self.history_of_time = np.zeros((seconds_in_experiment,), dtype=int)
		self.position_in_time = 0
		self.number_of_connections = 0

	# when called gets a connection for the user if it is available
	def get_connection_stream_and_disconnect(self, global_clock):
		# if instance is blocked running an operation a get isn't possible
		if(global_clock < self.position_in_time):
			return
		# can only get a connection if state at time is 0
		if(self.history_of_time[global_clock] != 0):
			return
		# calculation connection time
		connection_time_amount = self.getting_a_random_normal(mean_connection_time, 
			sigma_connection_time, min_connection_time, max_connection_time)
		self.set_history_values(connection_time_amount, self.CONNECTED_STATE)

		# getting here is an increase in the number of connections to instance
		self.number_of_connections += 1

		# calculation streaming time
		streaming_time_amount = self.getting_a_random_normal(mean_streaming_time, 
			sigma_streaming_time, min_streaming_time, max_streaming_time)
		self.set_history_values(streaming_time_amount, self.STREAMING_STATE)

		# calculation disconnection/cleanup and back into pool time
		disconnection_cleanup_back_in_pool_time_amount = self.getting_a_random_normal(
			mean_disconnection_time, sigma_disconnection_time, 
			min_disconnection_time, max_disconnection_time)
		self.set_history_values(streaming_time_amount, self.DISCONNECT_CLEANUP_STATE)


	# set history values with the input states
	def set_history_values(self, number_of_seconds_to_update, state_value):
		for second in range(number_of_seconds_to_update):
			# check if experiment endtime passed
			if self.position_in_time + second >= seconds_in_experiment:
				self.position_in_time += number_of_seconds_to_update
				return
			position_in_history = self.position_in_time + second
			self.history_of_time[position_in_history] = state_value
		# move the time forward
		self.position_in_time += number_of_seconds_to_update


	# time getting a connection
	def getting_a_random_normal(self, mu, sigma, min_amount_of_time, max_amount_of_time):
		curr_normal = int(np.random.normal(mu, sigma))
		if(curr_normal < min_amount_of_time):
			return min_amount_of_time
		if(curr_normal > max_amount_of_time):
			return max_amount_of_time
		return curr_normal

	def get_instance_id(self):
		return self.id_num
	
	def get_number_of_connections_to_instance(self):
		return self.number_of_connections

	def get_time_array(self):
		return self.history_of_time


# ticks time forward in the model
def run_model_through_time(instance_list):
	# ticking time forward one second at a time
	for curr_second_in_global_time in range(seconds_in_experiment):
		for curr_instance in instance_list:
			curr_instance.get_connection_stream_and_disconnect(curr_second_in_global_time)


# Creates the given number of instances
def setup_instances():
	instance_list = list()
	for x in range(aws_instances):
		created_instance = AwsInstance(x)
		instance_list.append(created_instance)
	return instance_list


# Visualizes information about the model
def create_output(instance_list):
	total_connections = 0
	for curr_instance in instance_list:
		# print("instance ID:", curr_instance.get_instance_id())
		# print("instance Number of connections over", hours_model_runs, "hours: ", curr_instance.get_number_of_connections_to_instance())
		total_connections += curr_instance.get_number_of_connections_to_instance()
	print("")
	print("--------------------------------")
	print("")
	print("VARIABLES INPUT TO MODEL")
	print("number of hours",hours_model_runs)
	print("number of instances:",aws_instances)
	print("cost per instance:",aws_one_instance_cost_per_hour)
	print("")
	print("seconds on average to connect: ",mean_connection_time)
	print("seconds of standard deviation",sigma_connection_time)
	print("seconds minimum for a connection",min_connection_time)
	print("seconds maximum for a connection",max_connection_time)
	print("")
	print("seconds on average to stream",mean_streaming_time)
	print("seconds of standard deviation",sigma_streaming_time)
	print("seconds minimum for an entire stream session",min_streaming_time)
	print("seconds maximum for an entire stream session",max_streaming_time)
	print("")
	print("seconds on average to disconnect, cleanup, back in pool",mean_disconnection_time)
	print("seconds of standard deviation",sigma_disconnection_time)
	print("seconds minimum for a disconnect, cleanup, back in pool",min_disconnection_time)
	print("seconds maximum for a disconnect, cleanup, back in pool",max_disconnection_time)
	print("")
	print("--------------------------------")
	print("")
	print("OUTPUT FROM MODEL")
	print("total connections to all instances: ", total_connections)
	total_cost = aws_instances * aws_one_instance_cost_per_hour * hours_model_runs
	print("total cost: ", total_cost)
	print("cost per connection: ", total_cost * 1.0 / total_connections)
	print("average connections per instance over", hours_model_runs, "hour(s) is", total_connections * 1.0 / aws_instances)
	print("")
	print("--------------------------------")
	print("")

# Called from main.. Creates instances, runs model, then outputs
def run_model():
	# create instances
	instances_list = setup_instances()
	# run the model through time
	run_model_through_time(instances_list)
	create_output(instances_list)


# main
def main():
	run_model()


# start
if __name__== "__main__":
  main()