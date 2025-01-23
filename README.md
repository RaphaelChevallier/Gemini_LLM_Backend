# AI-Powered BE Solutions Codebase

Welcome to the AI-Powered Solutions Codebase! This repository is a collection of innovative projects that leverage advanced AI models to provide intelligent solutions across various domains. Each project is designed to run independently, making it easy to deploy and manage on a VPS server.

## Overview

This codebase is built around the use of AI models, particularly those from Vertex AI, to enhance and automate complex tasks. The projects within this repository utilize generative models to process and analyze data, provide insights, and interact with users in a human-like manner.

## Key Components

1. **Chat History Management**: 
   - Utilizes ChromaDB to store and manage chat histories.
   - AI models analyze and retrieve relevant past interactions to enhance user experience.

2. **Real Estate Strategy Development**:
   - Converts PDF documents into text and processes them to develop real estate strategies.
   - Uses AI to split text into meaningful chunks and store them in a vector database for efficient retrieval.

3. **Mock Interviews**:
   - Simulates real-world interview scenarios using AI models.
   - Provides feedback and guidance to users based on their code submissions and interactions.

4. **Trading Analysis**:
   - Analyzes stock market data to provide insights and trading strategies.
   - Uses AI to generate content and make informed decisions based on historical and current market data.

## AI Models

The codebase primarily uses Vertex AI's generative models, such as "gemini-1.0-pro", to power its applications. These models are capable of understanding and generating human-like text, making them ideal for tasks that require natural language processing and interaction.

### How It Works

- **Generative Models**: These models are used to generate responses, analyze text, and provide insights based on the input data. They are integrated into various components to enhance functionality and user interaction.

- **ChromaDB**: A vector database that stores and retrieves data efficiently. It is used to manage chat histories and real estate strategies, allowing for quick access to relevant information.

- **PDF Processing**: The codebase includes utilities to convert PDF documents into text, which is then processed and analyzed by AI models to extract valuable insights.

## Running the Projects

Each project in this codebase can be run independently, making it easy to deploy on a VPS server. Here's how you can get started:

1. **Environment Setup**: Ensure you have the necessary environment set up. Configure your `.env` file with the required credentials and settings.

2. **Dependencies**: Install the dependencies listed in `requirements.txt` using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Applications**: Navigate to the respective project directory and execute the main script. Each project is designed to run independently, allowing you to deploy them on separate VPS servers if needed.

## Conclusion

This codebase offers a robust set of AI-powered solutions that can be easily deployed and managed. Whether you're looking to enhance user interactions, develop strategic insights, or simulate real-world scenarios, this repository provides the tools and models to achieve your goals.