import multiprocessing

def run_peer():
    import subprocess
    subprocess.run(["python3", "peer.py"])

def run_app():
    import subprocess
    subprocess.run(["python3", "run_app.py"])


if __name__ == "__main__":
    # Create processes for each script
    peer_process = multiprocessing.Process(target=run_peer)
    app_process = multiprocessing.Process(target=run_app)
    
    # Start both processes
    peer_process.start()
    app_process.start()
    
    # Join the processes (wait for them to finish)
    peer_process.join()
    app_process.join()
