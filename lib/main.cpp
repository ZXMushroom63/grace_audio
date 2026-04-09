#include <windows.h>
#include <iostream>
#include <vector>
#include <set>
#include <filesystem>
#include <fstream>
#include <string>
#include <sstream>
#include <unordered_set>
#include <algorithm>
#include <chrono>
#include <thread>
#include <random>
#include <map>
namespace fs = std::filesystem;


std::string up_next = "";
std::wstring ExpandPath(const std::wstring& inputPath) {
    DWORD size = ExpandEnvironmentStringsW(inputPath.c_str(), NULL, 0);
    
    if (size == 0) {
        return L"";
    }

    std::wstring expandedPath;
    expandedPath.resize(size);

    if (ExpandEnvironmentStringsW(inputPath.c_str(), &expandedPath[0], size)) {
        expandedPath.pop_back(); 
        return expandedPath;
    }

    return L"";
}

std::unordered_set<size_t> getDataSet() {
    std::unordered_set<size_t> data_set;
    std::ifstream file("lib\\db.txt");

    if (!file.is_open()) {
        std::cerr << "Error: Could not open db.txt in the current directory." << std::endl;
        return data_set;
    }

    std::string line;
    while (std::getline(file, line)) {
        size_t comment_pos = line.find('#');
        
        std::string content = line.substr(0, comment_pos);

        std::stringstream ss(content);
        size_t value;
        if (ss >> value) {
            data_set.insert(value);
        }
    }

    file.close();

    std::cout << "Successfully loaded " << data_set.size() << " unique entries." << std::endl;

    return data_set;
}

void reroll_music(std::vector<std::string> oggs) {
    int idx = 0;
    auto iter = std::find(oggs.begin(), oggs.end(), up_next);
    if (iter != oggs.end()) {
        idx = std::distance(oggs.begin(), iter);
    }
    up_next = oggs[(idx + 1 % oggs.size())];
}

int main() {
    std::map<size_t, std::string> CUSTOMS = {
        {2259632, "special_lobby.ogg"},
        {875794, "special_dyson_vacuum.ogg"},
        {556944, "special_carnation.ogg"},
        {587519, "special_random_ass_scream.ogg"}
    };

    std::map<std::string, size_t> CUSTOMS_REVERSE;
    std::map<size_t, std::string> CUSTOMS_FINAL;
    
    for (auto const& [id, filename] : CUSTOMS) {
        CUSTOMS_REVERSE[filename] = id;
    }

    std::vector<std::string> oggs;
    std::string selectall = "";

    fs::path current_dir = fs::current_path() / "playlist_cache";

    if (!fs::exists(current_dir)) {
        std::cerr << "Warning: playlist_cache directory not found." << std::endl;
    } else {
        for (const auto& entry : fs::directory_iterator(current_dir)) {
            if (entry.is_regular_file() && entry.path().extension() == ".ogg") {
                std::string filename = entry.path().filename().string();
                std::string full_path = entry.path().string();

                if (filename == "special_selectall.ogg") {
                    selectall = full_path;
                    break; 
                }

                if (CUSTOMS_REVERSE.count(filename)) {
                    std::cout << "  - Registered: " << filename << " [SPECIAL]" << std::endl;
                    CUSTOMS_FINAL[CUSTOMS_REVERSE[filename]] = full_path;
                } else {
                    std::cout << "  - Registered: " << filename << std::endl;
                    oggs.push_back(full_path);
                }
            }
        }
    }

    if (oggs.empty()) {
        std::cout << "First, put your songs in the PLAYLIST folder\n"
                  << "Then, run UPDATE_PLAYLIST.bat\n"
                  << "Finally, close this window, and run RUN.bat\n"
                  << "(full instructions in HOW_TO_USE.txt)" << std::endl;
        
        std::this_thread::sleep_for(std::chrono::seconds(1000));
        return 0;
    }

    std::random_device rd;
    std::mt19937 g(rd());
    std::shuffle(oggs.begin(), oggs.end(), g);
    up_next = oggs[0];


    SetPriorityClass(GetCurrentProcess(), HIGH_PRIORITY_CLASS);
    if (!SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_HIGHEST)) {
        std::cerr << "Failed to set thread priority. Error: " << GetLastError() << std::endl;
    } else {
        std::cout << "Thread priority set to HIGHEST." << std::endl;
    }

    std::unordered_set<size_t> targetSizes = getDataSet();
    std::wstring rawPath = L"%TEMP%\\Roblox\\sounds";
    std::wstring fullPath = ExpandPath(rawPath);
    std::wcout << L"Hooking into: " << fullPath << std::endl;
    HANDLE hDir = CreateFileW(fullPath.c_str(), FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OVERLAPPED, NULL);

    HANDLE hIOCP = CreateIoCompletionPort(hDir, NULL, 0, 1); 

    std::vector<BYTE> buffer(64 * 1024);
    OVERLAPPED overlapped = {0};

    ReadDirectoryChangesW(hDir, buffer.data(), (DWORD)buffer.size(), TRUE,
        FILE_NOTIFY_CHANGE_FILE_NAME | FILE_NOTIFY_CHANGE_LAST_WRITE,
        NULL, &overlapped, NULL);

    while (true) {
        DWORD bytesTransferred;
        ULONG_PTR completionKey;
        LPOVERLAPPED pOverlapped;

        BOOL res = GetQueuedCompletionStatus(hIOCP, &bytesTransferred, &completionKey, &pOverlapped, INFINITE);

        if (res && bytesTransferred > 0) {
            BYTE* pBase = buffer.data();

            while (true) {
                FILE_NOTIFY_INFORMATION* pNotify = reinterpret_cast<FILE_NOTIFY_INFORMATION*>(pBase);
                
                std::wstring fileName(pNotify->FileName, pNotify->FileNameLength / sizeof(WCHAR));
                std::wstring fullFilePath = fullPath + L"\\" + fileName;

                if (std::filesystem::exists(fullFilePath)) {
                    uintmax_t fileSize = std::filesystem::file_size(fullFilePath);

                    if (targetSizes.find(fileSize) != targetSizes.end()) {
                        try {
                            fs::copy_file(up_next, fullFilePath, fs::copy_options::overwrite_existing);
                        } 
                        catch (const fs::filesystem_error& e) {
                            std::cerr << "OS Error: " << e.code().message() << std::endl;
                            std::cerr << "Path 1: " << e.path1() << std::endl;
                            if (!e.path2().empty()) std::cerr << "Path 2: " << e.path2() << std::endl;
                        }
                        catch (const std::exception& e) {
                            std::cerr << "Standard error: " << e.what() << std::endl;
                        }
                        std::wcout << up_next.c_str() << "\n";
                        reroll_music(oggs);
                        std::wcout << L"Match found! File: " << fileName
                                << L" Size: " << fileSize << L" bytes\n";
                    }
                }

                if (pNotify->NextEntryOffset == 0) break;
                pBase += pNotify->NextEntryOffset;
            }

            ReadDirectoryChangesW(hDir, buffer.data(), (DWORD)buffer.size(), TRUE,
                FILE_NOTIFY_CHANGE_FILE_NAME | FILE_NOTIFY_CHANGE_LAST_WRITE,
                NULL, &overlapped, NULL);

            std::flush(std::wcout);
        }
    }

    CloseHandle(hDir);
    return 0;
}