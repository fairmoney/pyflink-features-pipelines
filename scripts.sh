get_jars() {
  targetLocalDir="./jars"
  jarsListFilePath="./jars_list.txt"
  wget -c -P $targetLocalDir -i $jarsListFilePath
}