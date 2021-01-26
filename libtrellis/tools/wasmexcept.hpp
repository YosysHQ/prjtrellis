#if defined(__wasm)

#include <cstdint>
#include <iostream>

extern "C" {
// FIXME: WASI does not currently support exceptions.
void *__cxa_allocate_exception(size_t thrown_size) throw() { return malloc(thrown_size); }
bool __cxa_uncaught_exception() throw();
void __cxa_throw(void *thrown_exception, struct std::type_info *tinfo, void (*dest)(void *)) { std::terminate(); }
}

namespace boost {
struct source_location;
void throw_exception(std::exception const &e) { 
	std::cerr << "boost::exception(): " << e.what() << std::endl;
}
void throw_exception(std::exception const &e, boost::source_location const &) { 
	std::cerr << "boost::exception(): " << e.what() << std::endl;
}
} // namespace boost

#endif
