# WIP

Read setup/readme.md



# Future steps
1. Throughput. use Flink model.
    - Use a buffer to store streaming records, with a timeout plus record limit
    - Whenever one is hit, send buffered records downstream and reset buffer
    
2. Convert to pipelined model
    - 

    