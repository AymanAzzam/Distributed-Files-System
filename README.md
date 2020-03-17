# Distributed-File-System
We have master, data keepers and clients. Clients can ask master to upload/download videos then master reply with specific ip/port for data keeper to upload/download from it then Data keeper notify message that the process succeded.


# Master
Master processes are:
  1. Processes to interact with clients.
  2. Process to interact with data keepers.
  3. Process to receive alive message from datakeepers.
  4. Process to replicate data on different datakeepers.
  5. Main process to run all processes.

Master Shared Memories are:
  1. Lookup_table contains each file name and the data keepers contain that file.
  2. Available_stream_table contains each ip/port status for data keepers(available or busy).
  3. Alive_table contains status for each data keeper(alive or dead).

# Data keeper
Data keeper processes are:
  1. Processes to interact with clients and Master.
  2. Main process to run all processes.

## Run Master
We need first to write configuration file `config.txt` . Parameter are replica factor, replice_period, number of data keepers(n) and number of data keeper processes in that order then n pair of lines each two lines contain ip and start_port for the data keeper. Then run master.py and give it starting port and number of processes to connect with clients. For example:
```sh
$ python main.py 4444 1
```

## Run Data Keeper
Run data-keeper.py and give it starting port, number of processes to connect with clients/master and folder_name to upload/download files using it. For example:
```sh
$ python data_keeper.py 5556 3 dk1
```

## Run Client
Run client.py and give it master ip, master_start_port number of processes in master to interact with clients, folder_name to upload/download files using it and id for that user. For example:
```sh
$ python client.py 4444 1 client_data 6
```

## Team members
[Ayman Azzam](https://github.com/AymanAzzam)

[Amr Aboshama](https://github.com/Amr-Aboshama)

[Menna Fekry](https://github.com/MennaFekry)

[Reham Ali](https://github.com/rehamaali)
