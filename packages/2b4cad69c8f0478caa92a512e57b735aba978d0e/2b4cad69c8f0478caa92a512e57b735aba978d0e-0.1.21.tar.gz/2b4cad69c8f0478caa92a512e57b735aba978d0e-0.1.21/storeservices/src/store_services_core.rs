use log::*;
use pyo3::prelude::*;

#[cfg(target_os = "macos")]
mod posix_macos;
#[cfg(target_family = "windows")]
mod posix_windows;

#[derive(Debug)]
pub struct ServerError {
    pub code: i64,
    pub description: String,
}

#[derive(Debug)]
pub enum ProvisioningError {
    InvalidResponse,
    ServerError(ServerError),
}

#[derive(Debug)]
pub enum ADIError {
    Unknown(i32),
    ProvisioningError(ProvisioningError),
}

impl ADIError {
    pub fn resolve(error_number: i32) -> ADIError {
        ADIError::Unknown(error_number)
    }
}

use android_loader::android_library::AndroidLibrary;
use android_loader::sysv64_type;
use android_loader::{hook_manager, sysv64};
use anyhow::Result;
use libc::stat;
use libc::{size_t, ssize_t, AT_FDCWD, O_RDONLY, O_RDWR, O_WRONLY};
use std::collections::HashMap;
use std::ffi::{c_char, CString};
use std::os::raw::{c_int, c_void};
use std::path::PathBuf;

use std::str::Bytes; // Assuming you are using the libc crate for size_t

#[pyclass]
pub struct SynchronizeData {
    #[pyo3(get)]
    pub mid: Vec<u8>,
    #[pyo3(get)]
    pub srm: Vec<u8>,
}

#[pyclass]
pub struct StartProvisioningData {
    #[pyo3(get)]
    pub cpim: Vec<u8>,
    #[pyo3(get)]
    pub session: u32,
}

#[pyclass]
pub struct RequestOTPData {
    #[pyo3(get)]
    pub otp: Vec<u8>,
    #[pyo3(get)]
    pub mid: Vec<u8>,
}

#[pyclass]
pub struct SapSession {
    #[pyo3(get)]
    pub session: u64,
}

#[pyclass]
pub struct CertResult {
    #[pyo3(get)]
    pub cert: Vec<u8>,
}

#[pyclass]
pub struct KBSyncResult {
    #[pyo3(get)]
    pub kbsync: Vec<u8>,
}

#[pyclass]
pub struct SBSyncResult {
    #[pyo3(get)]
    pub sbsync: Vec<u8>,
}

#[pyclass]
pub struct FairPlaySession {
    #[pyo3(get)]
    pub session: u64,
}

#[pyclass]
pub struct StoreServicesCoreADIProxy {
    #[allow(dead_code)]
    store_services_core: AndroidLibrary<'static>,

    local_user_uuid: String,
    device_identifier: String,

    fairplay_context_id: u64,
    sap_context_id: u64,

    fairplay_init: sysv64_type!(
        fn(magic: u32, id: *const u8, path: *const u8, out_context_id: *mut u64) -> i32
    ),
    fairplay_load_library_with_path: sysv64_type!(fn(path: *const u8) -> i32),

    fairplay_set_android_id: sysv64_type!(fn(id: *const u8, length: u32) -> i32),
    fairplay_sync: sysv64_type!(fn() -> i32),

    fairplay_import_keybag: sysv64_type!(
        fn(
            context: u64,
            keybag: *const u8,
            keybag_length: u32,
            out_result: *mut u64,
            out_flag: *mut u64,
        ) -> i32
    ),

    fairplay_get_kbsync: sysv64_type!(
        fn(
            context: u64,
            ds_id: i64,
            zero: u32,
            flag: u64,
            out_kbsync: *mut *const u8,
            out_kbsync_length: *mut u32,
        ) -> i32
    ),

    fairplay_get_sbsync: sysv64_type!(
        fn(
            context: u64,
            ds_id: i64,
            flag: u32,
            mdm: *const u8,
            mdm_length: u32,
            out_kbsync: *mut *const u8,
            out_kbsync_length: *mut u32,
        ) -> i32
    ),

    adi_set_android_id: sysv64_type!(fn(id: *const u8, length: u32) -> i32),
    adi_set_provisioning_path: sysv64_type!(fn(path: *const u8) -> i32),

    adi_provisioning_erase: sysv64_type!(fn(ds_id: i64) -> i32),
    adi_synchronize: sysv64_type!(
        fn(
            ds_id: i64,
            sim: *const u8,
            sim_length: u32,
            out_mid: *mut *const u8,
            out_mid_length: *mut u32,
            out_srm: *mut *const u8,
            out_srm_length: *mut u32,
        ) -> i32
    ),
    adi_provisioning_process: sysv64_type!(fn(session: u32) -> i32),
    adi_provisioning_end: sysv64_type!(
        fn(session: u32, ptm: *const u8, ptm_length: u32, tk: *const u8, tk_length: u32) -> i32
    ),
    adi_provisioning_start: sysv64_type!(
        fn(
            ds_id: i64,
            spim: *const u8,
            spim_length: u32,
            out_cpim: *mut *const u8,
            out_cpim_length: *mut u32,
            out_session: *mut u32,
        ) -> i32
    ),
    adi_get_login_code: sysv64_type!(fn(ds_id: i64) -> i32),
    adi_dispose: sysv64_type!(fn(ptr: *const u8) -> i32),
    adi_otp_request: sysv64_type!(
        fn(
            ds_id: i64,
            out_mid: *mut *const u8,
            out_mid_size: *mut u32,
            out_otp: *mut *const u8,
            out_otp_size: *mut u32,
        ) -> i32
    ),

    sap_init: sysv64_type!(fn(out_sap_session: *mut u64, id: *const u8) -> i32),

    sap_exchange: sysv64_type!(
        fn(
            flag: u32,
            guid: *const u8,
            sap_session: u64,
            sap_setup_cert: *const u8,
            sap_cert_length: u32,
            out_cert_info: *mut *const u8,
            out_cert_length: *mut u32,
            out_server_state: *mut i32,
        ) -> i32
    ),
    sap_sign: sysv64_type!(
        fn(
            sap_session: u64,
            data: *const u8,
            data_length: u32,
            action_signature: *mut *const u8,
            action_signature_length: *mut u32,
        ) -> i32
    ),
    sap_prime_signature: sysv64_type!(
        fn(
            sap_context: u32,
            flag: u32,
            data: u32,
            data_length: u32,
            action_signature: u32,
            action_signature_length: u32,
        ) -> i32
    ),
    sap_verify: sysv64_type!(
        fn(sap_context: u32, data: u32, data_length: u32, zero_one: u32, zero_two: u32) -> i32
    ),
}

#[pymethods]
impl StoreServicesCoreADIProxy {
    #[new]
    pub fn new(library_path: String, provisioning_path: String) -> PyResult<Self> {
        Self::with_custom_provisioning_path(library_path, provisioning_path)
    }

    #[staticmethod]
    pub fn with_custom_provisioning_path(
        library_path: String,
        provisioning_path: String,
    ) -> Result<Self, PyErr> {
        let lib_path = PathBuf::from(library_path);
        let prov_path = PathBuf::from(provisioning_path);

        info!(
            "Initializing StoreServicesCoreADIProxy with library path {} and provisioning path {}",
            lib_path.to_str().unwrap(),
            prov_path.to_str().unwrap(),
        );

        // Should be safe if the library is correct.
        unsafe {
            LoaderHelpers::setup_hooks();

            if !lib_path.exists() {
                warn!(
                    "Library path {} does not exist, creating it",
                    lib_path.to_str().unwrap()
                );

                std::fs::create_dir_all(&lib_path)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)))?;
            }

            if !prov_path.exists() {
                warn!(
                    "Provisioning path {} does not exist, creating it",
                    prov_path.to_str().unwrap()
                );

                std::fs::create_dir_all(&prov_path)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)))?;
            }

            let library_path = lib_path
                .canonicalize()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)))?;

            #[cfg(target_arch = "x86_64")]
            const ARCH: &str = "x86_64";
            #[cfg(target_arch = "x86")]
            const ARCH: &str = "x86";
            #[cfg(target_arch = "arm")]
            const ARCH: &str = "armeabi-v7a";
            #[cfg(target_arch = "aarch64")]
            const ARCH: &str = "arm64-v8a";

            let native_library_path = library_path.join("lib").join(ARCH);

            let path = native_library_path.join("libstoreservicescore.so");
            let path_str = path.to_str().ok_or_else(|| {
                PyErr::new::<pyo3::exceptions::PyValueError, _>("Path conversion failed")
            })?;

            let store_services_core = AndroidLibrary::load(path_str).map_err(|_e| {
                PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
                    "Failed to load Android Library for arch {} on path {}",
                    ARCH, path_str
                ))
            })?;

            let cert_sap_init: sysv64_type!(
                fn(out_sap_context_id: *mut u64, device_guid: *mut u8) -> i32
            ) = std::mem::transmute(store_services_core.get_symbol("cp2g1b9ro").ok_or(
                PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to get symbol cp2g1b9ro"),
            )?);

            let adi_load_library_with_path: sysv64_type!(fn(path: *const u8) -> i32) =
                std::mem::transmute(store_services_core.get_symbol("kq56gsgHG6").ok_or(
                    PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol kq56gsgHG6",
                    ),
                )?);

            let adi_set_provisioning_path: sysv64_type!(fn(path: *const u8) -> i32) =
                std::mem::transmute(store_services_core.get_symbol("nf92ngaK92").ok_or(
                    PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol nf92ngaK92",
                    ),
                )?);

            let fairplay_load_library_with_path: sysv64_type!(fn(path: *const u8) -> i32) =
                std::mem::transmute(store_services_core.get_symbol("N8jdR29h").ok_or(
                    PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol N8jdR29h",
                    ),
                )?);

            let native_lib_path =
                CString::new(native_library_path.to_str().ok_or(PyErr::new::<
                    pyo3::exceptions::PyValueError,
                    _,
                >(
                    "Failed to convert path to string",
                ))?)
                .unwrap();

            let prov_path = prov_path
                .canonicalize()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)))?;

            assert_eq!(
                (adi_load_library_with_path)(native_lib_path.as_ptr() as *const u8),
                0
            );

            assert_eq!(
                (fairplay_load_library_with_path)(native_lib_path.as_ptr() as *const u8),
                0
            );

            let adi_set_android_id =
                store_services_core
                    .get_symbol("Sph98paBcz")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol Sph98paBcz",
                    ))?;

            let fairplay_init = store_services_core
                .get_symbol("XtCqEf5X")
                .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "Failed to get symbol XtCqEf5X",
                ))?;

            let fairplay_set_android_id =
                store_services_core
                    .get_symbol("bsawCXd")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol bsawCXd",
                    ))?;

            let fairplay_sync =
                store_services_core
                    .get_symbol("jk24uiwqrg")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol bsawCXd",
                    ))?;

            let fairplay_import_keybag =
                store_services_core
                    .get_symbol("ha0dkchaters6")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol ha0dkchaters6",
                    ))?;

            let fairplay_get_kbsync =
                store_services_core
                    .get_symbol("Mt76Vq80ux")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol Mt76Vq80ux",
                    ))?;

            let fairplay_get_sbsync =
                store_services_core.get_symbol("V3lNO").ok_or(PyErr::new::<
                    pyo3::exceptions::PyValueError,
                    _,
                >(
                    "Failed to get symbol Mt76Vq80ux",
                ))?;

            let adi_provisioning_erase =
                store_services_core
                    .get_symbol("p435tmhbla")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol p435tmhbla",
                    ))?;

            let adi_synchronize =
                store_services_core
                    .get_symbol("tn46gtiuhw")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol tn46gtiuhw",
                    ))?;

            let adi_provisioning_process =
                store_services_core
                    .get_symbol("fy34trz2st")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol fy34trz2st",
                    ))?;

            let adi_provisioning_end =
                store_services_core
                    .get_symbol("uv5t6nhkui")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol uv5t6nhkui",
                    ))?;

            let adi_provisioning_start =
                store_services_core
                    .get_symbol("rsegvyrt87")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol rsegvyrt87",
                    ))?;

            let adi_get_login_code =
                store_services_core
                    .get_symbol("aslgmuibau")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol aslgmuibau",
                    ))?;

            let adi_dispose = store_services_core
                .get_symbol("jk24uiwqrg")
                .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "Failed to get symbol jk24uiwqrg",
                ))?;

            let adi_otp_request =
                store_services_core
                    .get_symbol("qi864985u0")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol qi864985u0",
                    ))?;

            let cert_sap_exchange =
                store_services_core
                    .get_symbol("Mib5yocT")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol Mib5yocT",
                    ))?;

            let cert_sap_sign =
                store_services_core
                    .get_symbol("Fc3vhtJDvr")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol Fc3vhtJDvr",
                    ))?;

            let cert_sap_prime_signature =
                store_services_core
                    .get_symbol("jfkdDAjba3jd")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol jfkdDAjba3jd",
                    ))?;

            let cert_sap_verify =
                store_services_core
                    .get_symbol("gLg1CWr7p")
                    .ok_or(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Failed to get symbol gLg1CWr7p",
                    ))?;

            let proxy = StoreServicesCoreADIProxy {
                store_services_core,

                sap_context_id: 0,
                fairplay_context_id: 0,

                local_user_uuid: String::new(),
                device_identifier: String::new(),

                // fairplay_get_support_info: std::mem::transmute(fairplay_get_support_info),
                fairplay_init: std::mem::transmute(fairplay_init),
                fairplay_sync: std::mem::transmute(fairplay_sync),
                fairplay_load_library_with_path: std::mem::transmute(
                    fairplay_load_library_with_path,
                ),
                fairplay_set_android_id: std::mem::transmute(fairplay_set_android_id),
                fairplay_import_keybag: std::mem::transmute(fairplay_import_keybag),
                fairplay_get_kbsync: std::mem::transmute(fairplay_get_kbsync),
                fairplay_get_sbsync: std::mem::transmute(fairplay_get_sbsync),

                adi_set_android_id: std::mem::transmute(adi_set_android_id),
                adi_set_provisioning_path: std::mem::transmute(adi_set_provisioning_path),

                adi_provisioning_erase: std::mem::transmute(adi_provisioning_erase),
                adi_synchronize: std::mem::transmute(adi_synchronize),
                adi_provisioning_process: std::mem::transmute(adi_provisioning_process),
                adi_provisioning_end: std::mem::transmute(adi_provisioning_end),
                adi_provisioning_start: std::mem::transmute(adi_provisioning_start),
                adi_get_login_code: std::mem::transmute(adi_get_login_code),
                adi_dispose: std::mem::transmute(adi_dispose),
                adi_otp_request: std::mem::transmute(adi_otp_request),

                sap_init: std::mem::transmute(cert_sap_init),
                sap_exchange: std::mem::transmute(cert_sap_exchange),
                sap_sign: std::mem::transmute(cert_sap_sign),
                sap_prime_signature: std::mem::transmute(cert_sap_prime_signature),
                sap_verify: std::mem::transmute(cert_sap_verify),
            };

            Ok(proxy)
        }
    }

    fn erase_provisioning(&mut self, ds_id: i64) -> PyResult<()> {
        let result = (self.adi_provisioning_erase)(ds_id);
        if result == 0 {
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to erase provisioning: {}",
                result
            )))
        }
    }

    fn synchronize(&mut self, ds_id: i64, sim: &[u8]) -> PyResult<SynchronizeData> {
        unsafe {
            let sim_size = sim.len() as u32;
            let sim_ptr = sim.as_ptr();

            let mut mid_size: u32 = 0;
            let mut mid_ptr: *const u8 = std::ptr::null();
            let mut srm_size: u32 = 0;
            let mut srm_ptr: *const u8 = std::ptr::null();

            let result = (self.adi_synchronize)(
                ds_id,
                sim_ptr,
                sim_size,
                &mut mid_ptr,
                &mut mid_size,
                &mut srm_ptr,
                &mut srm_size,
            );

            match result {
                0 => {
                    let mut mid = vec![0; mid_size as usize];
                    let mut srm = vec![0; srm_size as usize];

                    mid.copy_from_slice(std::slice::from_raw_parts(mid_ptr, mid_size as usize));
                    srm.copy_from_slice(std::slice::from_raw_parts(srm_ptr, srm_size as usize));

                    (self.adi_dispose)(mid_ptr);
                    (self.adi_dispose)(srm_ptr);

                    Ok(SynchronizeData { mid, srm })
                }
                err => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "{:#?}",
                    err
                ))),
            }
        }
    }

    fn process_provisioning_session(&mut self, session: u32) -> PyResult<()> {
        let result = (self.adi_provisioning_process)(session);
        if result == 0 {
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to process provisioning session: {}",
                result
            )))
        }
    }

    fn end_provisioning(&mut self, session: u32, ptm: &[u8], tk: &[u8]) -> PyResult<()> {
        let ptm_size = ptm.len() as u32;
        let ptm_ptr = ptm.as_ptr();

        let tk_size = tk.len() as u32;
        let tk_ptr = tk.as_ptr();

        let result = (self.adi_provisioning_end)(session, ptm_ptr, ptm_size, tk_ptr, tk_size);
        if result == 0 {
            let result_prc = (self.adi_provisioning_process)(session);
            if result_prc == 0 {
                Ok(())
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "Failed to process provisioning session: {}",
                    result_prc
                )))
            }
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to end provisioning: {}",
                result
            )))
        }
    }

    fn start_provisioning(&mut self, ds_id: i64, spim: &[u8]) -> PyResult<StartProvisioningData> {
        unsafe {
            let spim_size = spim.len() as u32;
            let spim_ptr = spim.as_ptr();

            let mut cpim_size: u32 = 0;
            let mut cpim_ptr: *const u8 = std::ptr::null();

            let mut session: u32 = 0;

            let result = (self.adi_provisioning_start)(
                ds_id,
                spim_ptr,
                spim_size,
                &mut cpim_ptr,
                &mut cpim_size,
                &mut session,
            );

            match result {
                0 => {
                    let mut cpim = vec![0; cpim_size as usize];

                    cpim.copy_from_slice(std::slice::from_raw_parts(cpim_ptr, cpim_size as usize));

                    (self.adi_dispose)(cpim_ptr);

                    (self.fairplay_sync)();
                    Ok(StartProvisioningData { cpim, session })
                }
                err => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "{:#?}",
                    err
                ))),
            }
        }
    }

    fn is_machine_provisioned(&self, ds_id: i64) -> bool {
        (self.adi_get_login_code)(ds_id) == 0
    }

    fn request_otp(&self, ds_id: i64) -> PyResult<RequestOTPData> {
        unsafe {
            let mut mid_size: u32 = 0;
            let mut mid_ptr: *const u8 = std::ptr::null();
            let mut otp_size: u32 = 0;
            let mut otp_ptr: *const u8 = std::ptr::null();

            let result = (self.adi_otp_request)(
                ds_id,
                &mut mid_ptr,
                &mut mid_size,
                &mut otp_ptr,
                &mut otp_size,
            );

            match result {
                0 => {
                    let mut mid = vec![0; mid_size as usize];
                    let mut otp = vec![0; otp_size as usize];

                    mid.copy_from_slice(std::slice::from_raw_parts(mid_ptr, mid_size as usize));
                    otp.copy_from_slice(std::slice::from_raw_parts(otp_ptr, otp_size as usize));

                    (self.adi_dispose)(mid_ptr);
                    (self.adi_dispose)(otp_ptr);

                    Ok(RequestOTPData { mid, otp })
                }
                err => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "{:#?}",
                    err
                ))),
            }
        }
    }

    fn set_local_user_uuid(&mut self, local_user_uuid: String) {
        self.local_user_uuid = local_user_uuid.clone();
    }

    fn set_device_identifier(&mut self, device_identifier: String) -> PyResult<()> {
        self.device_identifier = device_identifier.clone();

        let result = self.set_identifier(device_identifier);

        if result.is_ok() {
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to set device identifier: {}",
                result.unwrap_err()
            )))
        }
    }

    fn set_fairplay_device_identifier(&mut self, device_identifier: String) -> PyResult<()> {
        let result = self.set_fair_play_identifier(device_identifier);

        if result.is_ok() {
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to set device identifier: {}",
                result.unwrap_err()
            )))
        }
    }

    fn get_local_user_uuid(&self) -> String {
        self.local_user_uuid.clone()
    }

    fn get_device_identifier(&self) -> String {
        self.device_identifier.clone()
    }

    fn get_serial_number(&self) -> String {
        arc4random().to_string()
    }

    fn set_identifier(&mut self, identifier: String) -> PyResult<()> {
        let str = CString::new(identifier.to_string()).unwrap();
        let len = identifier.len() as u32;

        let result = (self.adi_set_android_id)(str.as_ptr() as *const u8, len);

        if result == 0 {
            debug!("Set identifier to {}", identifier);
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to set identifier: {}",
                result
            )))
        }
    }

    fn set_fair_play_identifier(&mut self, identifier: String) -> PyResult<()> {
        let str = CString::new(identifier.to_string()).unwrap();
        let len = identifier.len() as u32;

        let result = (self.fairplay_set_android_id)(str.as_ptr() as *const u8, len);

        if result == 0 {
            debug!("Set fairplay identifier to {}", identifier);
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to set fairplay identifier: {}",
                result
            )))
        }
    }

    fn import_keybag(&mut self, context: u64, keybag_data: &[u8]) -> PyResult<()> {
        unsafe {
            let keybag_size = keybag_data.len() as u32;
            let keybag_ptr = keybag_data.as_ptr();

            let mut result: u64 = 0;
            let mut flag: u64 = 0;

            let result = (self.fairplay_import_keybag)(
                context,
                keybag_ptr,
                keybag_size,
                &mut result,
                &mut flag,
            );

            if result == 0 {
                debug!("Imported keybag");
                Ok(())
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "Failed to import keybag: {}",
                    result
                )))
            }
        }
    }

    fn get_kbsync(&mut self, context: u64, ds_id: i64, flag: u64) -> PyResult<KBSyncResult> {
        unsafe {
            let mut kbsync: *const u8 = std::ptr::null();
            let mut kbsync_length: u32 = 0;

            let result = (self.fairplay_get_kbsync)(
                context,
                ds_id,
                0,
                flag,
                &mut kbsync,
                &mut kbsync_length,
            );

            if result == 0 {
                println!("Got kbsync with length {}", kbsync_length);
                let mut kbsync_data = vec![0; kbsync_length as usize];

                kbsync_data
                    .copy_from_slice(std::slice::from_raw_parts(kbsync, kbsync_length as usize));

                Ok(KBSyncResult {
                    kbsync: kbsync_data,
                })
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "Failed to get kbsync: {}",
                    result
                )))
            }
        }
    }

    fn get_sbsync(
        &mut self,
        context: u64,
        ds_id: i64,
        flag: u32,
        mdm_data: &[u8],
    ) -> PyResult<SBSyncResult> {
        unsafe {
            let mut sbsync: *const u8 = std::ptr::null();
            let mut sbsync_length: u32 = 0;

            let mdm_size = mdm_data.len() as u32;
            let mdm_ptr = mdm_data.as_ptr();

            let result = (self.fairplay_get_sbsync)(
                context,
                ds_id,
                flag,
                mdm_ptr,
                mdm_size,
                &mut sbsync,
                &mut sbsync_length,
            );

            if result == 0 {
                println!("Got sbsync with length {}", sbsync_length);
                let mut sbsync_data = vec![0; sbsync_length as usize];

                sbsync_data
                    .copy_from_slice(std::slice::from_raw_parts(sbsync, sbsync_length as usize));

                Ok(SBSyncResult {
                    sbsync: sbsync_data,
                })
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "Failed to get kbsync: {}",
                    result
                )))
            }
        }
    }

    fn set_provisioning_path(&mut self, provisioning_path: String) -> PyResult<()> {
        let prov_path = PathBuf::from(provisioning_path);

        let prov_path = prov_path
            .canonicalize()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)))?;

        let prov_lib_path_str = prov_path.to_str().ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>("Path conversion failed")
        })?;

        let result = (self.adi_set_provisioning_path)(prov_lib_path_str.as_ptr() as *const u8);

        if result == 0 {
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to set provisioning path: {}",
                result
            )))
        }
    }

    fn set_fireplay_path(
        &mut self,
        provisioning_path: String,
        device: Vec<u8>,
    ) -> PyResult<FairPlaySession> {
        let prov_path = PathBuf::from(provisioning_path);

        let prov_path = prov_path
            .canonicalize()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)))?;

        let prov_lib_path_str = prov_path.to_str().ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>("Path conversion failed")
        })?;

        let mut session: u64 = 0;

        info!("Setting fairplay path to {}", prov_lib_path_str);

        let result = (self.fairplay_init)(
            0,
            device.as_ptr() as *const u8,
            prov_lib_path_str.as_ptr() as *const u8,
            &mut session,
        );

        if result == 0 {
            Ok(FairPlaySession { session })
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to set fairplay path: {}",
                result
            )))
        }
    }

    fn setup_sap(&mut self) -> PyResult<SapSession> {
        let mut device_guid = &self.device_identifier[0..16];

        let mut session: u64 = 0;

        let result = (self.sap_init)(&mut session, device_guid.as_ptr());

        if result == 0 {
            debug!("SAP initialized");
            Ok(SapSession { session })
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to initialize SAP: {}",
                result
            )))
        }
    }

    fn exchange_sap(
        &mut self,
        sap_session: u64,
        sap_cert: &[u8],
        identifier: String,
        is_reg: bool,
    ) -> PyResult<CertResult> {
        unsafe {
            let cert_size = sap_cert.len() as u32;
            let cert_ptr = sap_cert.as_ptr();
            let mut device = CString::new(identifier.to_string()).unwrap();

            let mut cert_out: *const u8 = std::ptr::null();
            let mut cert_out_size: u32 = 0;

            let mut serverState: i32 = -1;

            let result = if is_reg {
                (self.sap_exchange)(
                    0xD2,
                    device.as_ptr() as *const u8,
                    sap_session,
                    cert_ptr,
                    cert_size,
                    &mut cert_out,
                    &mut cert_out_size,
                    &mut serverState,
                )
            } else {
                (self.sap_exchange)(
                    0xC8,
                    device.as_ptr() as *const u8,
                    sap_session,
                    cert_ptr,
                    cert_size,
                    &mut cert_out,
                    &mut cert_out_size,
                    &mut serverState,
                )
            };

            if result == 0 {
                let mut cert = vec![0; cert_out_size as usize];

                cert.copy_from_slice(std::slice::from_raw_parts(cert_out, cert_out_size as usize));

                Ok(CertResult { cert: cert })
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "Failed to exchange SAP: {}",
                    result
                )))
            }
        }
    }

    fn sign(&mut self, sap_session: u64, data_to_sign: String) -> PyResult<CertResult> {
        unsafe {
            let mut data = CString::new(data_to_sign.to_string()).unwrap();

            let data_size = data_to_sign.len() as u32;
            let data_ptr = data.as_ptr();

            let mut cert_out: *const u8 = std::ptr::null();
            let mut cert_out_size: u32 = 0;

            let result = (self.sap_sign)(
                sap_session,
                data_ptr as *const u8,
                data_size,
                &mut cert_out,
                &mut cert_out_size,
            );

            if result == 0 {
                let mut cert = vec![0; cert_out_size as usize];

                cert.copy_from_slice(std::slice::from_raw_parts(cert_out, cert_out_size as usize));

                Ok(CertResult { cert: cert })
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "Failed to sign data: {}",
                    result
                )))
            }
        }
    }
}

#[pymodule]
fn storeservices(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    pyo3_log::init();

    m.add_class::<StoreServicesCoreADIProxy>()?;

    // Add other classes or functions to the module
    Ok(())
}
struct LoaderHelpers;

use rand::Rng;

#[cfg(all(target_family = "unix", not(target_os = "macos")))]
use libc::{
    access, chmod, close, free, fstat, fstatat, ftruncate, getpid, gettimeofday, getuid, lstat,
    malloc, mkdir, mmap, mprotect, open, prctl, read, strncpy, umask, write,
};
#[cfg(target_os = "macos")]
use posix_macos::*;

static mut ERRNO: i32 = 0;

#[allow(unreachable_code)]
#[sysv64]
unsafe fn __errno_location() -> *mut i32 {
    ERRNO = std::io::Error::last_os_error().raw_os_error().unwrap_or(0);
    &mut ERRNO
}

#[sysv64]
fn arc4random() -> u32 {
    rand::thread_rng().gen()
}

#[sysv64]
unsafe fn __system_property_get(_name: *const c_char, value: *mut c_char) -> i32 {
    *value = '0' as c_char;

    info!("__system_property_get called with name: {}", _name as u64);

    return 1;
}

#[sysv64]
unsafe fn hooked_fstatat(
    dirfd: c_int,
    pathname: *const c_char,
    statbuf: *mut stat,
    flags: c_int,
) -> c_int {
    let path = if !pathname.is_null() {
        std::ffi::CStr::from_ptr(pathname)
            .to_string_lossy()
            .into_owned()
    } else {
        String::from("NULL")
    };

    if dirfd == AT_FDCWD || path.starts_with('/') {
        // Absolute path or relative to current working directory
        println!("fstatat called on file: {}", path);
    } else {
        // Relative path to the directory referred by dirfd
        println!(
            "fstatat called on file relative to dirfd {}: {}",
            dirfd, path
        );
    }

    // Call the actual fstatat function
    fstatat(dirfd, pathname, statbuf, flags)
}

#[sysv64]
unsafe fn wrapped_open(path: *const c_char, oflag: c_int, mode: c_int) -> c_int {
    // Perform any additional operations here. For example, log the path if it's not null.
    unsafe {
        if !path.is_null() {
            let path_str = std::ffi::CStr::from_ptr(path).to_string_lossy();
            info!("Opening file: {}", path_str);
        }

        // Call the actual open function from libc
        open(path, oflag, mode)
    }
}

#[cfg(target_family = "windows")]
use posix_windows::*;

impl LoaderHelpers {
    pub fn setup_hooks() {
        fn read_wrapper(fd: c_int, buf: *mut c_void, count: size_t) -> ssize_t {
            // Log the call to `read`
            info!("read called with fd: {}, count: {}", fd, count);

            // Call the original `read` function
            unsafe { read(fd, buf, count) }
        }

        let mut hooks = HashMap::new();
        hooks.insert("arc4random".to_owned(), arc4random as usize);
        hooks.insert("access".to_owned(), access as usize);
        hooks.insert("chmod".to_owned(), chmod as usize);
        hooks.insert("mmap".to_owned(), mmap as usize);
        hooks.insert("mprotect".to_owned(), mprotect as usize);
        hooks.insert("prctl".to_owned(), prctl as usize);
        hooks.insert("getpid".to_owned(), getpid as usize);
        hooks.insert("getuid".to_owned(), getuid as usize);
        hooks.insert(
            "__system_property_get".to_owned(),
            __system_property_get as usize,
        );
        hooks.insert("__errno".to_owned(), __errno_location as usize);
        hooks.insert("close".to_owned(), close as usize);
        hooks.insert("free".to_owned(), free as usize);
        hooks.insert("fstatat".to_owned(), hooked_fstatat as usize);
        hooks.insert("fstat".to_owned(), fstat as usize);
        hooks.insert("ftruncate".to_owned(), ftruncate as usize);
        hooks.insert("gettimeofday".to_owned(), gettimeofday as usize);
        hooks.insert("lstat".to_owned(), lstat as usize);
        hooks.insert("malloc".to_owned(), malloc as usize);
        hooks.insert("mkdir".to_owned(), mkdir as usize);
        hooks.insert("open".to_owned(), wrapped_open as usize);
        hooks.insert("read".to_owned(), read_wrapper as usize);
        hooks.insert("strncpy".to_owned(), strncpy as usize);
        hooks.insert("umask".to_owned(), umask as usize);
        hooks.insert("write".to_owned(), write as usize);

        hook_manager::add_hooks(hooks);
    }
}

#[cfg(test)]
mod tests {
    use crate::store_services_core::StoreServicesCoreADIProxy;

    use anyhow::{Ok, Result};
    use log::info;
    use std::path::PathBuf;

    #[test]
    fn setup_test() -> Result<()> {
        let path = String::from("anisette_test");
        let other_path = String::from("anisette_test");

        let ssc_adi_proxy = StoreServicesCoreADIProxy::new(path, other_path).unwrap();

        let result = (ssc_adi_proxy.adi_get_login_code)(-2);

        info!("Result: {}", result);
        Ok(())
        // ssc_adi_proxy.set_device_identifier("test".to_string())?;
    }
}
