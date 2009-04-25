/* 
  Direct copy backend 
*/

#include <fstream>
#include <iostream>
#include <stdio.h>
#include <string.h>
#include "boost/filesystem/operations.hpp"
#include "copy.h"
using namespace std;

int main(int argc, char **argv) {
  add_file(argv[1], argv[2]);
  /*boost::filesystem::path full_path( boost::filesystem::initial_path<boost::filesystem::path>() );
  full_path = boost::filesystem::system_complete( boost::filesystem::path( argv[1], boost::filesystem::native ) );
  std::cout << "\nIn directory: "
            << full_path.native_directory_string() << "\n\n";
  boost::filesystem::directory_iterator end_iter;
  for ( boost::filesystem::directory_iterator dir_itr( full_path );
        dir_itr != end_iter;
        ++dir_itr ) {
    cout << dir_itr->leaf() << "\n";
  }*/
  return 0;
}

int add_file(const char *src,
             const char *dst) {
  /* Adds a single file */
  ifstream                          infile;
  ofstream                          outfile;
  char                              *buffer;
  int                               src_size;
  int                               status;
  int                               count(0);
  printf("Copying %s to %s\n", src, dst);
  status = STATUS_OK;
  // open at end so tellg() gets file size
  infile.open(src, ios::binary|ios::ate);
  outfile.open(dst, ios::binary);
  src_size = infile.tellg();
  // seek to beginning since we opened at end
  infile.seekg (0, ios::beg);
  //printf("Source size: %d\n", src_size);
  buffer = new char[BUFFER_SIZE];
  while ( (status == STATUS_OK) && (!infile.eof()) ) {
    // reads BUFFER_SIZE of data info buffer
    infile.read(buffer, BUFFER_SIZE);
    outfile.write(buffer, infile.gcount());
    count += infile.gcount();
    //printf("Current progress: %dMB\n", (count/1024/1024));
  }
  infile.close();
  outfile.close();
  // deletes buffer and its contents
  delete[] buffer;
  return(status);
}

int remove_file() {
  /* Removes a single file */

}

int add_folder() {
  /* Removes a folder and its contents */

}

int remove_folder() {
  /* Removes a folder and its contents */

}

int mkdir() {
  /* Creates an empty directory */

}

int rmdir() {
  /* Removes an empty directory */

}
