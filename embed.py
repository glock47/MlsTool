#!/usr/bin/python

import sys, getopt
from progressbar import ProgressBar
from lib.System import System
from lib.TextModel import TextModel


def main(argv):
    text = ["javascript_ruby",
            "c_java",
            "c_objective-c",
            "c_shell",
            "c#_javascript",
            "c_javascript",
            "c_objective-c_python",
            "c_ruby_shell",
            "javascript_shell",
            "javascript_python",
            "objective-c_perl_shell",
            "c#_javascript",
            "javascript_ruby",
            "javascript_python",
            "objective-c_ruby",
            "c_c++_objective-c",
            "c++_javascript",
            "c++_javascript",
            "c_c++_java",
            "c++_java_python",
            "c++_objective-c_shell",
            "c++_javascript",
            "objective-c_ruby",
            "c_ruby_shell",
            "java_javascript_objective-c",
            "c_shell",
            "objective-c_ruby",
            "java_shell",
            "javascript_objective-c",
            "c++_java_javascript",
            "c_c++_objective-c",
            "c_c++_objective-c",
            "html_javascript_shell",
            "java_shell",
            "html_javascript_java",
            "java_python",
            "html_java_javascript_shell",
            "html_javascript_java_c",
            "java_javascript",
            "c++_cmake_shell"]

    print ("text num = %d" %len(text))
    
    format_text = []
    unique_lang = []
    feature_num = 0
    for combo in text:
        combo = combo.replace ("_", " ")
        print (combo)

        nt = []
        for lang in combo.split(" "):
            nt.append (lang)
            if (lang not in unique_lang):
                unique_lang.append (lang)

        if (len(nt) > feature_num):
            feature_num = len(nt)

        format_text.append (nt)

    print ("Unique Languages:" + str(unique_lang))
    print ("Format_text" + str(format_text))
    TM = TextModel ()
    document_w2c = TM.document_word2vec (format_text, feature_num)

    print ("document_w2c = %d" %len(document_w2c))
    for w2c in document_w2c:
        value = 0
        for val in w2c:
            value = value + abs(val)
        print (value)
    

if __name__ == "__main__":
   main(sys.argv[1:])
