
del build /s /f /q
rmdir build /s/q
mkdir build

del firmware /s /f /q
rmdir firmware /s /q
mkdir firmware
cd firmware
mkdir beta
mkdir webcontrolcnc
mkdir holey

cd ../build
SET beta_firmware_repo=https://github.com/WebControlCNC/Firmware.git
SET beta_firmware_sha=bf4350ffd9bc154832505fc0125abd2c4c04dba7
git clone %beta_firmware_repo% firmware/beta
cd firmware/beta
git checkout %beta_firmware_sha%
pio run -e megaatmega2560

copy .pio/build/megaatmega2560/firmware.hex ~/WebControl/firmware/beta/beta-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex

cd ../..

SET webcontrolcnc_firmware_repo=https://github.com/WebControlCNC/Firmware.git
SET webcontrolcnc_firmware_sha=e1e0d020fff1f4f7c6b403a26a85a16546b7e15b
git clone %webcontrolcnc_firmware_repo% firmware/maslowcnc
cd firmware/webcontrolcnc
git checkout %webcontrolcnc_firmware_sha%
pio run -e megaatmega2560
copy .pio/build/megaatmega2560/firmware.hex ~/WebControl/firmware/webcontrolcnc/webcontrolcnc-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex

cd ../..

SET holey_firmware_repo=https://github.com/webcontrolcnc/Firmware.git
SET holey_firmware_sha=950fb23396171cbd456c2d4149455cc45f5e6bc3
git clone %holey_firmware_repo% firmware/holey
cd firmware/holey
git checkout %holey_firmware_sha%
pio run -e megaatmega2560
copy .pio/build/megaatmega2560/firmware.hex ~\WebControlfirmware/holey/holey-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex
