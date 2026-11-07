Name:		bean-validation-api
Version:	2.0.1.Final
Release:	1
Summary:	Bean Validation API
Group:		Development/Java
License:	ASL 2.0
URL:		https://beanvalidation.org/
Source0:	https://github.com/jakartaee/validation/archive/refs/tags/%{version}.tar.gz#/validation-api-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name validation-api --link %{name}

Obsoletes:	%{name}-javadoc < %{version}-%{release}

%description
Bean Validation is the API for declaring constraints on Java objects.
2.0.1.Final is the last release of javax.validation:validation-api.
The automatic module name stays java.validation. Tests are skipped.

%prep
%autosetup -n validation-%{version}
python - <<'PY'
from pathlib import Path

java_files = list(Path("src/main/java").rglob("*.java"))
if len(java_files) != 97:
    raise SystemExit("java files " + str(len(java_files)))
Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>javax.validation</groupId>
  <artifactId>validation-api</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>Bean Validation API</name>
  <description>Bean Validation API</description>
  <url>https://beanvalidation.org/</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.source>1.8</maven.compiler.source>
    <maven.compiler.target>1.8</maven.compiler.target>
  </properties>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <source>1.8</source>
          <target>1.8</target>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
        <configuration>
          <archive>
            <manifestEntries>
              <Automatic-Module-Name>java.validation</Automatic-Module-Name>
            </manifestEntries>
          </archive>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>validation-api</artifactId>",
    "<version>%{version}</version>",
    "<source>1.8</source>",
    "<target>1.8</target>",
    "java.validation",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("testng", "maven-bundle-plugin", "SNAPSHOT", "<release>", "jakarta.validation"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
if list(Path(".").rglob("*.jar")):
    raise SystemExit("prebuilt jar remains")
PY

%build -a
cat > manifest-addition <<'EOF'
Automatic-Module-Name: java.validation
EOF
jar ufm target/validation-api-%{version}.jar manifest-addition
java --module-path target/validation-api-%{version}.jar --describe-module java.validation > module-describe.txt
# A versioned jar prints "name@version ... automatic", not "name automatic".
grep -q '^java.validation' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }

%files -f .mfiles
%doc README.md license.txt
