%define native_snapshot 02.02.2015
%define lang_snapshot 02.02.2015
%define armips_snapshot 20.01.2015

Summary:	Sony PlayStation Portable (PSP) emulator
Name:		ppsspp
Version:	1.6.1
Release:	1
License:	GPLv2+
Group:		Emulators
Url:		http://www.ppsspp.org
# From git by tag https://github.com/hrydgard/ppsspp
Source0:	%{name}-%{version}.tar.gz
# Deprecated. Don't use. (penguin)
# From git https://github.com/hrydgard/native
#Source1:	native-%{native_snapshot}.tar.bz2
# From git https://github.com/hrydgard/ppsspp-lang
Source2:	ppsspp-lang-%{lang_snapshot}.tar.bz2
# From git https://github.com/Kingcom/armips
Source3:	armips-%{armips_snapshot}.tar.bz2
Patch0:		ppsspp-0.8-git-version.patch
Patch1:		ppsspp-0.9.9.1-datapath.patch
# Can work with any ffmpeg but requires ffmpeg with Atrac3+ support for ingame music
Patch2:		ppsspp-1.0-ffmpeg.patch
BuildRequires:	cmake
BuildRequires:	imagemagick
BuildRequires:	ffmpeg-devel
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(glu)
#Requires system libpng17, otherwise uses internal static build
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(sdl2)
BuildRequires:	pkgconfig(zlib)

%description
PPSSPP is a cross-platform Sony PlayStation Portable (PSP) emulator.

PPSSPP can run your PSP games on your PC in full HD resolution, and play
them on Android too. It can even upscale textures that would otherwise be
too blurry as they were made for the small screen of the original PSP.

%files
%{_gamesbindir}/%{name}-sdl
%{_datadir}/applications/%{name}.desktop
%{_iconsdir}/hicolor/*/apps/%{name}.png
%{_gamesdatadir}/%{name}

#----------------------------------------------------------------------------

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
sed s,"unknown_version","%{version}",g -i git-version.cmake

# Unpack external libraries from Native sub-project
rm -rf lang
#tar -xf %{SOURCE1}
#mv native-%{native_snapshot} native
tar -xf %{SOURCE2}
mv ppsspp-lang-%{lang_snapshot} lang
pushd ext
rm -rf armips
tar -xf %{SOURCE3}
mv armips-%{armips_snapshot} armips
popd

%build
# segfaults with default -O2 optimization
%global optflags %{optflags} -O0
%cmake \
	-DHEADLESS:BOOL=OFF \
	-DUSE_FFMPEG:BOOL=ON
%make

%install
mkdir -p %{buildroot}%{_gamesbindir}
install -m 0755 build/PPSSPPSDL %{buildroot}%{_gamesbindir}/%{name}-sdl
mkdir -p %{buildroot}%{_gamesdatadir}/%{name}
cp -r build/assets %{buildroot}%{_gamesdatadir}/%{name}
cp -r lang %{buildroot}%{_gamesdatadir}/%{name}/assets/

# install menu entry
mkdir -p %{buildroot}%{_datadir}/applications/
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << EOF
[Desktop Entry]
Name=PPSSPP
Comment=Sony PSP emulator
Exec=%{_gamesbindir}/%{name}-sdl
Icon=%{name}
Terminal=false
Type=Application
Categories=Game;Emulator;
EOF

# install menu icons
for N in 16 32 48 64 128;
do
convert assets/icon-114.png -scale ${N}x${N} $N.png;
install -D -m 0644 $N.png %{buildroot}%{_iconsdir}/hicolor/${N}x${N}/apps/%{name}.png
done

