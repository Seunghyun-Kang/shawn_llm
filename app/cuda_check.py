import torch

# Check if CUDA is available
if torch.cuda.is_available():
	print("CUDA is available.")
	# Print the CUDA device count
	print(f"Number of CUDA devices: {torch.cuda.device_count()}")
	# Print the name of the current CUDA device
	print(f"Current CUDA device name: {torch.cuda.get_device_name(torch.cuda.current_device())}")
else:
	print("CUDA is not available.")

print("pytorch version")
print(torch.__version__)