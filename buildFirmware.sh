#!/bin/bash
rm -rf build
mkdir build
rm -rf firmware
mkdir firmware
cd firmware
mkdir beta
mkdir webcontrolcnc
mkdir holey

cd ../build
beta_firmware_repo=https://github.com/WebControlCNC/Firmware.git
beta_firmware_sha=bf4350ffd9bc154832505fc0125abd2c4c04dba7
git clone $beta_firmware_repo firmware/beta
cd firmware/beta
git checkout $beta_firmware_sha
pio lib install "Servo"
pio run -e megaatmega2560
mv .pio/build/megaatmega2560/firmware.hex ./beta-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex

cd ../..

webcontrolcnc_firmware_repo=https://github.com/WebControlCNC/Firmware.git
webcontrolcnc_firmware_sha=e1e0d020fff1f4f7c6b403a26a85a16546b7e15b
git clone $webcontrolcnc_firmware_repo firmware/webcontrolcnc
cd firmware/webcontrolcnc
git checkout $webcontrolcnc_firmware_sha
pio lib install "Servo"
pio run -e megaatmega2560
mv .pio/build/megaatmega2560/firmware.hex ./webcontrolcnc-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex

cd ../..

holey_firmware_repo=https://github.com/WebControlCNC/Firmware.git
holey_firmware_sha=950fb23396171cbd456c2d4149455cc45f5e6bc3
git clone $holey_firmware_repo firmware/holey
cd firmware/holey
git checkout $holey_firmware_sha
pio run -e megaatmega2560
mv .pio/build/megaatmega2560/firmware.hex ./holey-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex
