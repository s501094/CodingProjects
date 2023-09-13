#include <iostream>
#include <string>
#include <curl/curl.h>
#include "nlohmann/json.hpp"
#include <Python.h>

std::string speechToText(const std::string& audioFilePath) {
    // Initialize the Python interpreter
    Py_Initialize();

    // Import the Python module (e.g., 'whisper_asr.py')
    PyObject* pName = PyUnicode_DecodeFSDefault("whisper_asr");
    PyObject* pModule = PyImport_Import(pName);

    std::string transcription = "";

    if (pModule != NULL) {
        // Get the function from the module
        PyObject* pFunc = PyObject_GetAttrString(pModule, "get_transcription");
        
        if (PyCallable_Check(pFunc)) {
            PyObject* pArgs = PyTuple_Pack(1, PyUnicode_FromString(audioFilePath.c_str()));
            PyObject* pValue = PyObject_CallObject(pFunc, pArgs);

            if (pValue != NULL) {
                transcription = PyUnicode_AsUTF8(pValue);
                Py_DECREF(pValue);
            }
        }

        Py_DECREF(pFunc);
        Py_DECREF(pModule);
    }

    Py_DECREF(pName);

    // Finalize the Python interpreter
    Py_Finalize();

    return transcription;
}

// Callback to handle the response data
static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

// extracting the message from the response to declutter the output
std::string extractContent(const std::string& jsonResponse) {
    try {
        nlohmann::json j = nlohmann::json::parse(jsonResponse);

        if (j.contains("choices") && j["choices"].is_array() &&
            !j["choices"].empty() &&
            j["choices"][0].contains("message") &&
            j["choices"][0]["message"].is_object() &&
            j["choices"][0]["message"].contains("content") &&
            j["choices"][0]["message"]["content"].is_string()) {

            return j["choices"][0]["message"]["content"];
        } else {
            return "Unexpected JSON structure or missing keys.";
        }

    } catch (const std::exception& e) {
        return std::string("Error parsing JSON: ") + e.what();
    }
}

std::string chatWithGPT(const std::string& prompt) {
    CURL* curl = curl_easy_init();
    std::string readBuffer;

    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, "https://api.openai.com/v1/chat/completions");
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

        // Set headers
        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        headers = curl_slist_append(headers, "Authorization: Bearer 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");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        // Construct the payload using nlohmann::json
        nlohmann::json j;
        j["model"] = "gpt-3.5-turbo";


        // Create a series of messages
        nlohmann::json messages = nlohmann::json::array();
        messages.push_back({{"role", "system"}, {"content", "You are a helpful assistant."}});
        messages.push_back({{"role", "user"}, {"content", prompt}});
        j["messages"] = messages;

        j["max_tokens"] = 400;
        std::string payload = j.dump();

        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, payload.c_str());
        
        CURLcode res = curl_easy_perform(curl);

        if(res != CURLE_OK) {
            std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << std::endl;
        }

        curl_slist_free_all(headers); // free the header list
        curl_easy_cleanup(curl);
    }

    return extractContent(readBuffer); //extract only the message content
}

int main() {
    std::string prompt;
    
    while(true){
        std::cout << "What would you like to ask: ";
        std::getline(std::cin, prompt);
        
        if (prompt == "exit") {
            break;  // Exit the loop if "exit" is entered
        }

        std::string response = chatWithGPT(prompt);
        std::cout << "Response: " << std::endl << response << std::endl;
    }
    return 0;

}

