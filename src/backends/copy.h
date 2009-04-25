/* 
  Direct copy backend 
*/

#define API_VERSION 0.1
// 2^15 = 32KB
#define BUFFER_SIZE 32768

#define STATUS_OK 0
#define STATUS_ERROR 1
#define STATUS_NO_DISK_SPACE 2

int add_file
  (const char *src,
   const char *dst);
