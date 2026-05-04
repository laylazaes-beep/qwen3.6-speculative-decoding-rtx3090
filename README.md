# 📊 qwen3.6-speculative-decoding-rtx3090 - Test Qwen model speed on hardware

[![](https://img.shields.io/badge/Download_Benchmark_Package-blue)](https://github.com/laylazaes-beep/qwen3.6-speculative-decoding-rtx3090)

This repository hosts data from performance tests for the Qwen3.6 artificial intelligence model. It specifically examines how the model runs on an NVIDIA RTX 3090 graphics card. This project uses speculative decoding to analyze how different configuration settings affect the speed of the model.

## 🖥️ System Requirements

To run these tests, your computer needs specific hardware and software components. If your system does not meet these requirements, the software may not start or may run very slowly.

*   **Operating System**: Windows 10 or Windows 11.
*   **Graphics Card**: NVIDIA RTX 3090 with 24GB of video memory.
*   **Drivers**: Install the latest NVIDIA GPU drivers from the official website.
*   **Memory**: 32GB of system RAM recommended.
*   **Storage**: 50GB of free space on a Solid State Drive.
*   **Software**: Microsoft Visual C++ Redistributable for Visual Studio 2022.

## 📥 How to Get the Software

You must visit the project page to download the necessary files. This software does not require complex installation scripts. Follow these steps to obtain the toolset:

1. Visit the repository page here: [https://github.com/laylazaes-beep/qwen3.6-speculative-decoding-rtx3090](https://github.com/laylazaes-beep/qwen3.6-speculative-decoding-rtx3090).
2. Look for the green button labeled "Code" toward the top right side of the screen.
3. Select "Download ZIP" from the menu.
4. Save the file to your computer.
5. Right-click the downloaded folder and select "Extract All."

## ⚙️ Setting Up the Environment

The benchmark requires the CUDA Toolkit to communicate with your graphics card. If you have not used tools like this before, follow these instructions to prepare your machine:

1. Download the CUDA Toolkit installer from the official NVIDIA developer website.
2. Run the installer and follow the default prompts. 
3. Restart your computer after the installation completes.
4. Open the command prompt by typing "cmd" in the start menu search bar.
5. Type "nvidia-smi" and press Enter. If you see a table displaying your GPU information, your system is ready.

## 🚀 Running the Benchmarks

Once you have extracted the files, you can start the testing process. This repository provides several pre-configured files to test different ways the model processes information.

1. Open the folder where you extracted the project files.
2. Locate the file named "run_benchmark.bat." This script automatically handles the settings for the RTX 3090.
3. Double-click the file to start the process.
4. A black window will appear on your screen. Do not close this window.
5. The software will begin processing data. It will perform 19 different configuration tests to see how the model responds under varied conditions.

## 📈 Understanding the Results

After the process finishes, the software creates a folder named "results." Inside this folder, you will find two types of files:

*   **JSON Files**: These files contain raw data about the time it took for the model to generate text. You can open these with any text editor like Notepad.
*   **Plot Files**: These are image files that visualize the speed of the model. They show how well the N-gram cache and other draft models performed compared to standard setups.

The findings from this specific study show that on the RTX 3090, these speculative decoding variants do not currently offer a speed gain. These results are useful for researchers who want to see why certain hardware configurations handle these models differently.

## 🛠️ Troubleshooting Common Issues

If the software fails to run, check these common points of failure:

*   **Out of Memory Errors**: If the window closes immediately, your graphics card might be running out of memory. Close background applications like web browsers or video games before running the benchmark.
*   **Missing Files**: Ensure that you have extracted all files from the ZIP archive. If you run the script inside the ZIP folder, the software cannot locate the necessary data files.
*   **Driver Version**: Verify that you are using the most current drivers. Older drivers often lack the support necessary for modern machine learning libraries.
*   **Permissions**: Ensure your user account has permission to write files to the folder where you placed the benchmark data.

This project exists to archive the performance data of Qwen3.6. We provide all logs and scripts to ensure you can repeat these tests on your own hardware to verify the findings.