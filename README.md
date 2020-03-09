# Distributed-File-System
We have master, data keepers and clients. Clients can ask master to upload/download videos then master reply with specific ip/port for data keeper to upload/download from it then Data keeper notify message that the process succeded.

## Master
Master contains several processes. Processes to interact with clients and process to interact with data keepers. Master contains lookup_table that has each file name and the data keepers contain that file. Master contains available_table too that has each ip/port status for data keepers(available or busy).
