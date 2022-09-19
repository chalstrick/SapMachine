artifacts builderVersion:"1.1", {
    group "com.sap.sapmachine", {
        artifact "sapmachine-jdk_darwinintel64", {
            file "${gendir}/sapmachine-intel64-jdk.tar.gz", extension:"tar.gz"
            file "${gendir}/sapmachine-intel64-jdk.dmg", extension:"dmg"
        }
        artifact "sapmachine-jre_darwinintel64", {
            file "${gendir}/sapmachine-intel64-jre.tar.gz", extension:"tar.gz"
            file "${gendir}/sapmachine-intel64-jre.dmg", extension:"dmg"
        }
        artifact "sapmachine-symbols_darwinintel64", {
            file "${gendir}/sapmachine-intel64-symbols.tar.gz", extension:"tar.gz"
        }
        artifact "sapmachine-jdk_darwinaarch64", {
            file "${gendir}/sapmachine-aarch64-jdk.tar.gz", extension:"tar.gz"
            file "${gendir}/sapmachine-aarch64-jdk.dmg", extension:"dmg"
        }
        artifact "sapmachine-jre_darwinaarch64", {
            file "${gendir}/sapmachine-aarch64-jre.tar.gz", extension:"tar.gz"
            file "${gendir}/sapmachine-aarch64-jre.dmg", extension:"dmg"
        }
        artifact "sapmachine-symbols_darwinaarch64", {
            file "${gendir}/sapmachine-aarch64-symbols.tar.gz", extension:"tar.gz"
        }
    }
}
