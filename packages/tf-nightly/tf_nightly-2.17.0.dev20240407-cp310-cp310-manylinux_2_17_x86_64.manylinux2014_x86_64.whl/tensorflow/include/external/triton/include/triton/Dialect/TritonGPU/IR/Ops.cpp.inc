/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Op Definitions                                                             *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|* From: TritonGPUOps.td                                                      *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

#ifdef GET_OP_LIST
#undef GET_OP_LIST

::mlir::triton::gpu::AsyncBulkCommitGroupOp,
::mlir::triton::gpu::AsyncBulkWaitOp,
::mlir::triton::gpu::AsyncCommitGroupOp,
::mlir::triton::gpu::AsyncCopyGlobalToLocalOp,
::mlir::triton::gpu::AsyncWaitOp,
::mlir::triton::gpu::ConvertLayoutOp,
::mlir::triton::gpu::LocalAllocOp,
::mlir::triton::gpu::LocalDeallocOp,
::mlir::triton::gpu::LocalLoadOp,
::mlir::triton::gpu::MemDescSubviewOp,
::mlir::triton::gpu::SparseDotOp
#endif  // GET_OP_LIST

#ifdef GET_OP_CLASSES
#undef GET_OP_CLASSES


//===----------------------------------------------------------------------===//
// Local Utility Method Definitions
//===----------------------------------------------------------------------===//

namespace mlir {
namespace triton {
namespace gpu {

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonGPUOps0(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!((::llvm::isa<::mlir::triton::gpu::AsyncTokenType>(type)))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be variadic of async token type, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonGPUOps1(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!((::llvm::isa<::mlir::triton::gpu::AsyncTokenType>(type)))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be async token type, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonGPUOps2(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!(((::llvm::isa<::mlir::RankedTensorType>(type))) && ([](::mlir::Type elementType) { return ((elementType.isa<::mlir::triton::PointerType>())) && ([](::mlir::Type pointeeType) { return (true); }(elementType.cast<::mlir::triton::PointerType>().getPointeeType())); }(::llvm::cast<::mlir::ShapedType>(type).getElementType())))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be ranked tensor of ptr values, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonGPUOps3(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!((::llvm::isa<::mlir::triton::MemDescType>(type)))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be memory descriptor type (`::mlir::triton::MemDescType`) in Triton IR type system, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonGPUOps4(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!(((::llvm::isa<::mlir::TensorType>(type))) && ([](::mlir::Type elementType) { return (elementType.isSignlessInteger(1)); }(::llvm::cast<::mlir::ShapedType>(type).getElementType())))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be tensor of 1-bit signless integer values, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonGPUOps5(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!(((((type.isFloat8E4M3FNUZ())) || ((type.isFloat8E4M3FN())) || ((type.isFloat8E4M3B11FNUZ())) || ((type.isFloat8E5M2())) || ((type.isFloat8E5M2FNUZ())) || ((type.isF16())) || ((type.isBF16())) || ((type.isF32())) || ((type.isF64()))) || (((::llvm::isa<::mlir::RankedTensorType>(type))) && ([](::mlir::Type elementType) { return ((elementType.isFloat8E4M3FNUZ())) || ((elementType.isFloat8E4M3FN())) || ((elementType.isFloat8E4M3B11FNUZ())) || ((elementType.isFloat8E5M2())) || ((elementType.isFloat8E5M2FNUZ())) || ((elementType.isF16())) || ((elementType.isBF16())) || ((elementType.isF32())) || ((elementType.isF64())); }(::llvm::cast<::mlir::ShapedType>(type).getElementType())))) || ((((type.isSignlessInteger(1))) || ((type.isSignlessInteger(8))) || ((type.isSignlessInteger(16))) || ((type.isSignlessInteger(32))) || ((type.isSignlessInteger(64)))) || (((::llvm::isa<::mlir::RankedTensorType>(type))) && ([](::mlir::Type elementType) { return ((elementType.isSignlessInteger(1))) || ((elementType.isSignlessInteger(8))) || ((elementType.isSignlessInteger(16))) || ((elementType.isSignlessInteger(32))) || ((elementType.isSignlessInteger(64))); }(::llvm::cast<::mlir::ShapedType>(type).getElementType())))) || ((((type.isa<::mlir::triton::PointerType>())) && ([](::mlir::Type pointeeType) { return (true); }(type.cast<::mlir::triton::PointerType>().getPointeeType()))) || (((::llvm::isa<::mlir::RankedTensorType>(type))) && ([](::mlir::Type elementType) { return ((elementType.isa<::mlir::triton::PointerType>())) && ([](::mlir::Type pointeeType) { return (true); }(elementType.cast<::mlir::triton::PointerType>().getPointeeType())); }(::llvm::cast<::mlir::ShapedType>(type).getElementType())))) || (((type.isa<::mlir::triton::PointerType>())) && ([](::mlir::Type pointeeType) { return ((::llvm::isa<::mlir::RankedTensorType>(pointeeType))) && ([](::mlir::Type elementType) { return (((elementType.isFloat8E4M3FNUZ())) || ((elementType.isFloat8E4M3FN())) || ((elementType.isFloat8E4M3B11FNUZ())) || ((elementType.isFloat8E5M2())) || ((elementType.isFloat8E5M2FNUZ())) || ((elementType.isF16())) || ((elementType.isBF16())) || ((elementType.isF32())) || ((elementType.isF64()))) || (((elementType.isSignlessInteger(1))) || ((elementType.isSignlessInteger(8))) || ((elementType.isSignlessInteger(16))) || ((elementType.isSignlessInteger(32))) || ((elementType.isSignlessInteger(64)))) || (((elementType.isa<::mlir::triton::PointerType>())) && ([](::mlir::Type pointeeType) { return (true); }(elementType.cast<::mlir::triton::PointerType>().getPointeeType()))); }(::llvm::cast<::mlir::ShapedType>(pointeeType).getElementType())); }(type.cast<::mlir::triton::PointerType>().getPointeeType()))))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be floating-point or ranked tensor of floating-point values or integer or ranked tensor of integer values or ptr or ranked tensor of ptr values or ptr, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonGPUOps6(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!(((::llvm::isa<::mlir::RankedTensorType>(type))) && ([](::mlir::Type elementType) { return (((elementType.isFloat8E4M3FNUZ())) || ((elementType.isFloat8E4M3FN())) || ((elementType.isFloat8E4M3B11FNUZ())) || ((elementType.isFloat8E5M2())) || ((elementType.isFloat8E5M2FNUZ())) || ((elementType.isF16())) || ((elementType.isBF16())) || ((elementType.isF32())) || ((elementType.isF64()))) || (((elementType.isSignlessInteger(1))) || ((elementType.isSignlessInteger(8))) || ((elementType.isSignlessInteger(16))) || ((elementType.isSignlessInteger(32))) || ((elementType.isSignlessInteger(64)))) || (((elementType.isa<::mlir::triton::PointerType>())) && ([](::mlir::Type pointeeType) { return (true); }(elementType.cast<::mlir::triton::PointerType>().getPointeeType()))); }(::llvm::cast<::mlir::ShapedType>(type).getElementType())))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be ranked tensor of floating-point or integer or ptr values, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonGPUOps7(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!((type.isSignlessInteger(32)))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be variadic of 32-bit signless integer, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonGPUOps8(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!((::llvm::isa<::mlir::TensorOrMemDesc>(type)))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be TensorOrMemDesc instance, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonGPUOps9(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!(((::llvm::isa<::mlir::RankedTensorType>(type))) && ([](::mlir::Type elementType) { return (((elementType.isFloat8E4M3FNUZ())) || ((elementType.isFloat8E4M3FN())) || ((elementType.isFloat8E4M3B11FNUZ())) || ((elementType.isFloat8E5M2())) || ((elementType.isFloat8E5M2FNUZ())) || ((elementType.isF16())) || ((elementType.isBF16())) || ((elementType.isF32())) || ((elementType.isF64()))) || (((elementType.isSignlessInteger(1))) || ((elementType.isSignlessInteger(8))) || ((elementType.isSignlessInteger(16))) || ((elementType.isSignlessInteger(32))) || ((elementType.isSignlessInteger(64)))); }(::llvm::cast<::mlir::ShapedType>(type).getElementType())))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be ranked tensor of floating-point or integer values, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonGPUOps10(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!(((::llvm::isa<::mlir::RankedTensorType>(type))) && ([](::mlir::Type elementType) { return ((elementType.isSignlessInteger(1))) || ((elementType.isSignlessInteger(8))) || ((elementType.isSignlessInteger(16))) || ((elementType.isSignlessInteger(32))) || ((elementType.isSignlessInteger(64))); }(::llvm::cast<::mlir::ShapedType>(type).getElementType())))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be ranked tensor of integer values, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonGPUOps0(
    ::mlir::Attribute attr, ::llvm::StringRef attrName, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  if (attr && !(((::llvm::isa<::mlir::IntegerAttr>(attr))) && ((::llvm::cast<::mlir::IntegerAttr>(attr).getType().isSignlessInteger(32)))))
    return emitError() << "attribute '" << attrName
        << "' failed to satisfy constraint: 32-bit signless integer attribute";
  return ::mlir::success();
}
static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonGPUOps0(
    ::mlir::Operation *op, ::mlir::Attribute attr, ::llvm::StringRef attrName) {
  return __mlir_ods_local_attr_constraint_TritonGPUOps0(attr, attrName, [op]() {
    return op->emitOpError();
  });
}

static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonGPUOps1(
    ::mlir::Attribute attr, ::llvm::StringRef attrName, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  if (attr && !((::llvm::isa<::mlir::triton::CacheModifierAttr>(attr))))
    return emitError() << "attribute '" << attrName
        << "' failed to satisfy constraint: allowed 32-bit signless integer cases: 1, 2, 3, 4, 5, 6";
  return ::mlir::success();
}
static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonGPUOps1(
    ::mlir::Operation *op, ::mlir::Attribute attr, ::llvm::StringRef attrName) {
  return __mlir_ods_local_attr_constraint_TritonGPUOps1(attr, attrName, [op]() {
    return op->emitOpError();
  });
}

static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonGPUOps2(
    ::mlir::Attribute attr, ::llvm::StringRef attrName, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  if (attr && !((::llvm::isa<::mlir::triton::EvictionPolicyAttr>(attr))))
    return emitError() << "attribute '" << attrName
        << "' failed to satisfy constraint: allowed 32-bit signless integer cases: 1, 2, 3";
  return ::mlir::success();
}
static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonGPUOps2(
    ::mlir::Operation *op, ::mlir::Attribute attr, ::llvm::StringRef attrName) {
  return __mlir_ods_local_attr_constraint_TritonGPUOps2(attr, attrName, [op]() {
    return op->emitOpError();
  });
}

static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonGPUOps3(
    ::mlir::Attribute attr, ::llvm::StringRef attrName, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  if (attr && !((::llvm::isa<::mlir::BoolAttr>(attr))))
    return emitError() << "attribute '" << attrName
        << "' failed to satisfy constraint: bool attribute";
  return ::mlir::success();
}
static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonGPUOps3(
    ::mlir::Operation *op, ::mlir::Attribute attr, ::llvm::StringRef attrName) {
  return __mlir_ods_local_attr_constraint_TritonGPUOps3(attr, attrName, [op]() {
    return op->emitOpError();
  });
}
} // namespace gpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::gpu::AsyncBulkCommitGroupOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
AsyncBulkCommitGroupOpGenericAdaptorBase::AsyncBulkCommitGroupOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const ::mlir::EmptyProperties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_gpu.async_bulk_commit_group", odsAttrs.getContext());
}

AsyncBulkCommitGroupOpGenericAdaptorBase::AsyncBulkCommitGroupOpGenericAdaptorBase(AsyncBulkCommitGroupOp op) : AsyncBulkCommitGroupOpGenericAdaptorBase(op->getAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> AsyncBulkCommitGroupOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  return {index, 1};
}

::mlir::DictionaryAttr AsyncBulkCommitGroupOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

} // namespace detail
AsyncBulkCommitGroupOpAdaptor::AsyncBulkCommitGroupOpAdaptor(AsyncBulkCommitGroupOp op) : AsyncBulkCommitGroupOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult AsyncBulkCommitGroupOpAdaptor::verify(::mlir::Location loc) {
  return ::mlir::success();
}

std::pair<unsigned, unsigned> AsyncBulkCommitGroupOp::getODSOperandIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::operand_range AsyncBulkCommitGroupOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

std::pair<unsigned, unsigned> AsyncBulkCommitGroupOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range AsyncBulkCommitGroupOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

void AsyncBulkCommitGroupOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState) {
}

void AsyncBulkCommitGroupOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes) {
  assert(resultTypes.size() == 0u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void AsyncBulkCommitGroupOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 0u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 0u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

::mlir::LogicalResult AsyncBulkCommitGroupOp::verifyInvariantsImpl() {
  return ::mlir::success();
}

::mlir::LogicalResult AsyncBulkCommitGroupOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult AsyncBulkCommitGroupOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
  }
  return ::mlir::success();
}

void AsyncBulkCommitGroupOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
}

} // namespace gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::gpu::AsyncBulkCommitGroupOp)

namespace mlir {
namespace triton {
namespace gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::gpu::AsyncBulkWaitOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
AsyncBulkWaitOpGenericAdaptorBase::AsyncBulkWaitOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_gpu.async_bulk_wait", odsAttrs.getContext());
}

AsyncBulkWaitOpGenericAdaptorBase::AsyncBulkWaitOpGenericAdaptorBase(AsyncBulkWaitOp op) : AsyncBulkWaitOpGenericAdaptorBase(op->getDiscardableAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> AsyncBulkWaitOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  return {index, 1};
}

::mlir::DictionaryAttr AsyncBulkWaitOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

::mlir::IntegerAttr AsyncBulkWaitOpGenericAdaptorBase::getNumAttr() {
  auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().num);
  return attr;
}

uint32_t AsyncBulkWaitOpGenericAdaptorBase::getNum() {
  auto attr = getNumAttr();
  return attr.getValue().getZExtValue();
}

} // namespace detail
AsyncBulkWaitOpAdaptor::AsyncBulkWaitOpAdaptor(AsyncBulkWaitOp op) : AsyncBulkWaitOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult AsyncBulkWaitOpAdaptor::verify(::mlir::Location loc) {
  auto tblgen_num = getProperties().num; (void)tblgen_num;
  if (!tblgen_num) return emitError(loc, "'triton_gpu.async_bulk_wait' op ""requires attribute 'num'");

  if (tblgen_num && !(((::llvm::isa<::mlir::IntegerAttr>(tblgen_num))) && ((::llvm::cast<::mlir::IntegerAttr>(tblgen_num).getType().isSignlessInteger(32)))))
    return emitError(loc, "'triton_gpu.async_bulk_wait' op ""attribute 'num' failed to satisfy constraint: 32-bit signless integer attribute");
  return ::mlir::success();
}

std::pair<unsigned, unsigned> AsyncBulkWaitOp::getODSOperandIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::operand_range AsyncBulkWaitOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

std::pair<unsigned, unsigned> AsyncBulkWaitOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range AsyncBulkWaitOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::LogicalResult AsyncBulkWaitOp::setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  ::mlir::DictionaryAttr dict = ::llvm::dyn_cast<::mlir::DictionaryAttr>(attr);
  if (!dict) {
    emitError() << "expected DictionaryAttr to set properties";
    return ::mlir::failure();
  }

  {
    auto &propStorage = prop.num;
       auto attr = dict.get("num");
    if (attr || /*isRequired=*/true) {
      if (!attr) {
        emitError() << "expected key entry for num in DictionaryAttr to set "
                   "Properties.";
        return ::mlir::failure();
      }
      auto convertedAttr = ::llvm::dyn_cast<std::remove_reference_t<decltype(propStorage)>>(attr);
      if (convertedAttr) {
        propStorage = convertedAttr;
      } else {
        emitError() << "Invalid attribute `num` in property conversion: " << attr;
        return ::mlir::failure();
      }
    }
  }
  return ::mlir::success();
}

::mlir::Attribute AsyncBulkWaitOp::getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop) {
    ::mlir::SmallVector<::mlir::NamedAttribute> attrs;
    ::mlir::Builder odsBuilder{ctx};

    {
      const auto &propStorage = prop.num;
      if (propStorage)
        attrs.push_back(odsBuilder.getNamedAttr("num",
                                       propStorage));
    }

  if (!attrs.empty())
    return odsBuilder.getDictionaryAttr(attrs);
  return {};
}

llvm::hash_code AsyncBulkWaitOp::computePropertiesHash(const Properties &prop) {
  return llvm::hash_combine(
    llvm::hash_value(prop.num.getAsOpaquePointer()));
}

std::optional<mlir::Attribute> AsyncBulkWaitOp::getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name) {
    if (name == "num")
      return prop.num;
  return std::nullopt;
}

void AsyncBulkWaitOp::setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value) {
    if (name == "num") {
       prop.num = ::llvm::dyn_cast_or_null<std::remove_reference_t<decltype(prop.num)>>(value);
       return;
    }
}

void AsyncBulkWaitOp::populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs) {
    if (prop.num) attrs.append("num", prop.num);
}

::mlir::LogicalResult AsyncBulkWaitOp::verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
    {
      ::mlir::Attribute attr = attrs.get(getNumAttrName(opName));
      if (attr && ::mlir::failed(__mlir_ods_local_attr_constraint_TritonGPUOps0(attr, "num", emitError)))
        return ::mlir::failure();
    }
    return ::mlir::success();
}

::mlir::LogicalResult AsyncBulkWaitOp::readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state) {
  auto &prop = state.getOrAddProperties<Properties>(); (void)prop;
  if (::mlir::failed(reader.readAttribute(prop.num)))
    return ::mlir::failure();
  return ::mlir::success();
}

void AsyncBulkWaitOp::writeProperties(::mlir::DialectBytecodeWriter &writer) {
  auto &prop = getProperties(); (void)prop;
  writer.writeAttribute(prop.num);
}

::mlir::IntegerAttr AsyncBulkWaitOp::getNumAttr() {
  return ::llvm::cast<::mlir::IntegerAttr>(getProperties().num);
}

uint32_t AsyncBulkWaitOp::getNum() {
  auto attr = getNumAttr();
  return attr.getValue().getZExtValue();
}

void AsyncBulkWaitOp::setNumAttr(::mlir::IntegerAttr attr) {
  getProperties().num = attr;
}

void AsyncBulkWaitOp::setNum(uint32_t attrValue) {
  getProperties().num = ::mlir::Builder((*this)->getContext()).getIntegerAttr(::mlir::Builder((*this)->getContext()).getIntegerType(32), attrValue);
}

void AsyncBulkWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::IntegerAttr num) {
  odsState.getOrAddProperties<Properties>().num = num;
}

void AsyncBulkWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::IntegerAttr num) {
  odsState.getOrAddProperties<Properties>().num = num;
  assert(resultTypes.size() == 0u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void AsyncBulkWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, uint32_t num) {
  odsState.getOrAddProperties<Properties>().num = odsBuilder.getIntegerAttr(odsBuilder.getIntegerType(32), num);
}

void AsyncBulkWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, uint32_t num) {
  odsState.getOrAddProperties<Properties>().num = odsBuilder.getIntegerAttr(odsBuilder.getIntegerType(32), num);
  assert(resultTypes.size() == 0u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void AsyncBulkWaitOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 0u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 0u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

::mlir::LogicalResult AsyncBulkWaitOp::verifyInvariantsImpl() {
  auto tblgen_num = getProperties().num; (void)tblgen_num;
  if (!tblgen_num) return emitOpError("requires attribute 'num'");

  if (::mlir::failed(__mlir_ods_local_attr_constraint_TritonGPUOps0(*this, tblgen_num, "num")))
    return ::mlir::failure();
  return ::mlir::success();
}

::mlir::LogicalResult AsyncBulkWaitOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult AsyncBulkWaitOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
    if (failed(verifyInherentAttrs(result.name, result.attributes, [&]() {
        return parser.emitError(loc) << "'" << result.name.getStringRef() << "' op ";
      })))
      return ::mlir::failure();
  }
  return ::mlir::success();
}

void AsyncBulkWaitOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
}

} // namespace gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::gpu::AsyncBulkWaitOp)

namespace mlir {
namespace triton {
namespace gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::gpu::AsyncCommitGroupOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
AsyncCommitGroupOpGenericAdaptorBase::AsyncCommitGroupOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const ::mlir::EmptyProperties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_gpu.async_commit_group", odsAttrs.getContext());
}

AsyncCommitGroupOpGenericAdaptorBase::AsyncCommitGroupOpGenericAdaptorBase(AsyncCommitGroupOp op) : AsyncCommitGroupOpGenericAdaptorBase(op->getAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> AsyncCommitGroupOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  bool isVariadic[] = {true};
  int prevVariadicCount = 0;
  for (unsigned i = 0; i < index; ++i)
    if (isVariadic[i]) ++prevVariadicCount;

  // Calculate how many dynamic values a static variadic operand corresponds to.
  // This assumes all static variadic operands have the same dynamic value count.
  int variadicSize = (odsOperandsSize - 0) / 1;
  // `index` passed in as the parameter is the static index which counts each
  // operand (variadic or not) as size 1. So here for each previous static variadic
  // operand, we need to offset by (variadicSize - 1) to get where the dynamic
  // value pack for this static operand starts.
  int start = index + (variadicSize - 1) * prevVariadicCount;
  int size = isVariadic[index] ? variadicSize : 1;
  return {start, size};
}

::mlir::DictionaryAttr AsyncCommitGroupOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

} // namespace detail
AsyncCommitGroupOpAdaptor::AsyncCommitGroupOpAdaptor(AsyncCommitGroupOp op) : AsyncCommitGroupOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult AsyncCommitGroupOpAdaptor::verify(::mlir::Location loc) {
  return ::mlir::success();
}

std::pair<unsigned, unsigned> AsyncCommitGroupOp::getODSOperandIndexAndLength(unsigned index) {
  bool isVariadic[] = {true};
  int prevVariadicCount = 0;
  for (unsigned i = 0; i < index; ++i)
    if (isVariadic[i]) ++prevVariadicCount;

  // Calculate how many dynamic values a static variadic operand corresponds to.
  // This assumes all static variadic operands have the same dynamic value count.
  int variadicSize = (getOperation()->getNumOperands() - 0) / 1;
  // `index` passed in as the parameter is the static index which counts each
  // operand (variadic or not) as size 1. So here for each previous static variadic
  // operand, we need to offset by (variadicSize - 1) to get where the dynamic
  // value pack for this static operand starts.
  int start = index + (variadicSize - 1) * prevVariadicCount;
  int size = isVariadic[index] ? variadicSize : 1;
  return {start, size};
}

::mlir::Operation::operand_range AsyncCommitGroupOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

::mlir::Operation::operand_range AsyncCommitGroupOp::getInputTokens() {
  return getODSOperands(0);
}

::mlir::MutableOperandRange AsyncCommitGroupOp::getInputTokensMutable() {
  auto range = getODSOperandIndexAndLength(0);
  auto mutableRange = ::mlir::MutableOperandRange(getOperation(), range.first, range.second);
  return mutableRange;
}

std::pair<unsigned, unsigned> AsyncCommitGroupOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range AsyncCommitGroupOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::triton::gpu::AsyncTokenType> AsyncCommitGroupOp::getAsyncToken() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::AsyncTokenType>>(*getODSResults(0).begin());
}

void AsyncCommitGroupOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type asyncToken, ::mlir::ValueRange inputTokens) {
  odsState.addOperands(inputTokens);
  odsState.addTypes(asyncToken);
}

void AsyncCommitGroupOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 1u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

void AsyncCommitGroupOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);

  ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
  if (::mlir::succeeded(AsyncCommitGroupOp::inferReturnTypes(odsBuilder.getContext(),
          odsState.location, operands,
          odsState.attributes.getDictionary(odsState.getContext()),
          odsState.getRawProperties(),
          odsState.regions, inferredReturnTypes))) {
    assert(inferredReturnTypes.size() == 1u && "mismatched number of return types");
    odsState.addTypes(inferredReturnTypes);
  } else {
    ::llvm::report_fatal_error("Failed to infer result type(s).");
  }
}

::mlir::LogicalResult AsyncCommitGroupOp::verifyInvariantsImpl() {
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSOperands(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps0(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
  }
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSResults(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps1(*this, v.getType(), "result", index++)))
        return ::mlir::failure();
    }
  }
  return ::mlir::success();
}

::mlir::LogicalResult AsyncCommitGroupOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::LogicalResult AsyncCommitGroupOp::inferReturnTypes(::mlir::MLIRContext *context, ::std::optional<::mlir::Location> location, ::mlir::ValueRange operands, ::mlir::DictionaryAttr attributes, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions, ::llvm::SmallVectorImpl<::mlir::Type>&inferredReturnTypes) {
  inferredReturnTypes.resize(1);
  ::mlir::Builder odsBuilder(context);
  ::mlir::Type odsInferredType0 = odsBuilder.getType<::mlir::triton::gpu::AsyncTokenType>();
  inferredReturnTypes[0] = odsInferredType0;
  return ::mlir::success();
}

::mlir::ParseResult AsyncCommitGroupOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::llvm::SmallVector<::mlir::OpAsmParser::UnresolvedOperand, 4> inputTokensOperands;
  ::llvm::SMLoc inputTokensOperandsLoc;
  (void)inputTokensOperandsLoc;

  inputTokensOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperandList(inputTokensOperands))
    return ::mlir::failure();
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
  }
  ::mlir::Type odsBuildableType0 = parser.getBuilder().getType<::mlir::triton::gpu::AsyncTokenType>();
  result.addTypes(odsBuildableType0);
  if (parser.resolveOperands(inputTokensOperands, odsBuildableType0, inputTokensOperandsLoc, result.operands))
    return ::mlir::failure();
  return ::mlir::success();
}

void AsyncCommitGroupOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  _odsPrinter << ' ';
  _odsPrinter << getInputTokens();
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
}

} // namespace gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::gpu::AsyncCommitGroupOp)

namespace mlir {
namespace triton {
namespace gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::gpu::AsyncCopyGlobalToLocalOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
AsyncCopyGlobalToLocalOpGenericAdaptorBase::AsyncCopyGlobalToLocalOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_gpu.async_copy_global_to_local", odsAttrs.getContext());
}

AsyncCopyGlobalToLocalOpGenericAdaptorBase::AsyncCopyGlobalToLocalOpGenericAdaptorBase(AsyncCopyGlobalToLocalOp op) : AsyncCopyGlobalToLocalOpGenericAdaptorBase(op->getDiscardableAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> AsyncCopyGlobalToLocalOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  ::llvm::ArrayRef<int32_t> sizeAttr = getProperties().operandSegmentSizes;

  unsigned start = 0;
  for (unsigned i = 0; i < index; ++i)
    start += sizeAttr[i];
  return {start, sizeAttr[index]};
}

::mlir::DictionaryAttr AsyncCopyGlobalToLocalOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

::mlir::triton::CacheModifierAttr AsyncCopyGlobalToLocalOpGenericAdaptorBase::getCacheAttr() {
  auto attr = ::llvm::cast<::mlir::triton::CacheModifierAttr>(getProperties().cache);
  return attr;
}

::mlir::triton::CacheModifier AsyncCopyGlobalToLocalOpGenericAdaptorBase::getCache() {
  auto attr = getCacheAttr();
  return attr.getValue();
}

::mlir::triton::EvictionPolicyAttr AsyncCopyGlobalToLocalOpGenericAdaptorBase::getEvictAttr() {
  auto attr = ::llvm::cast<::mlir::triton::EvictionPolicyAttr>(getProperties().evict);
  return attr;
}

::mlir::triton::EvictionPolicy AsyncCopyGlobalToLocalOpGenericAdaptorBase::getEvict() {
  auto attr = getEvictAttr();
  return attr.getValue();
}

::mlir::BoolAttr AsyncCopyGlobalToLocalOpGenericAdaptorBase::getIsVolatileAttr() {
  auto attr = ::llvm::cast<::mlir::BoolAttr>(getProperties().isVolatile);
  return attr;
}

bool AsyncCopyGlobalToLocalOpGenericAdaptorBase::getIsVolatile() {
  auto attr = getIsVolatileAttr();
  return attr.getValue();
}

} // namespace detail
AsyncCopyGlobalToLocalOpAdaptor::AsyncCopyGlobalToLocalOpAdaptor(AsyncCopyGlobalToLocalOp op) : AsyncCopyGlobalToLocalOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult AsyncCopyGlobalToLocalOpAdaptor::verify(::mlir::Location loc) {
  auto tblgen_cache = getProperties().cache; (void)tblgen_cache;
  if (!tblgen_cache) return emitError(loc, "'triton_gpu.async_copy_global_to_local' op ""requires attribute 'cache'");
  auto tblgen_evict = getProperties().evict; (void)tblgen_evict;
  if (!tblgen_evict) return emitError(loc, "'triton_gpu.async_copy_global_to_local' op ""requires attribute 'evict'");
  auto tblgen_isVolatile = getProperties().isVolatile; (void)tblgen_isVolatile;
  if (!tblgen_isVolatile) return emitError(loc, "'triton_gpu.async_copy_global_to_local' op ""requires attribute 'isVolatile'");

  if (tblgen_cache && !((::llvm::isa<::mlir::triton::CacheModifierAttr>(tblgen_cache))))
    return emitError(loc, "'triton_gpu.async_copy_global_to_local' op ""attribute 'cache' failed to satisfy constraint: allowed 32-bit signless integer cases: 1, 2, 3, 4, 5, 6");

  if (tblgen_evict && !((::llvm::isa<::mlir::triton::EvictionPolicyAttr>(tblgen_evict))))
    return emitError(loc, "'triton_gpu.async_copy_global_to_local' op ""attribute 'evict' failed to satisfy constraint: allowed 32-bit signless integer cases: 1, 2, 3");

  if (tblgen_isVolatile && !((::llvm::isa<::mlir::BoolAttr>(tblgen_isVolatile))))
    return emitError(loc, "'triton_gpu.async_copy_global_to_local' op ""attribute 'isVolatile' failed to satisfy constraint: bool attribute");
  return ::mlir::success();
}

std::pair<unsigned, unsigned> AsyncCopyGlobalToLocalOp::getODSOperandIndexAndLength(unsigned index) {
  ::llvm::ArrayRef<int32_t> sizeAttr = getProperties().operandSegmentSizes;

  unsigned start = 0;
  for (unsigned i = 0; i < index; ++i)
    start += sizeAttr[i];
  return {start, sizeAttr[index]};
}

::mlir::Operation::operand_range AsyncCopyGlobalToLocalOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::RankedTensorType> AsyncCopyGlobalToLocalOp::getSrc() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(0).begin());
}

::mlir::TypedValue<::mlir::triton::MemDescType> AsyncCopyGlobalToLocalOp::getDst() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::triton::MemDescType>>(*getODSOperands(1).begin());
}

::mlir::TypedValue<::mlir::TensorType> AsyncCopyGlobalToLocalOp::getMask() {
  auto operands = getODSOperands(2);
  return operands.empty() ? ::mlir::TypedValue<::mlir::TensorType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::TensorType>>(*operands.begin());
}

::mlir::Value AsyncCopyGlobalToLocalOp::getOther() {
  auto operands = getODSOperands(3);
  return operands.empty() ? ::mlir::Value{} : ::llvm::cast<::mlir::Value>(*operands.begin());
}

::mlir::OpOperand &AsyncCopyGlobalToLocalOp::getSrcMutable() {
  auto range = getODSOperandIndexAndLength(0);
  return getOperation()->getOpOperand(range.first);
}

::mlir::OpOperand &AsyncCopyGlobalToLocalOp::getDstMutable() {
  auto range = getODSOperandIndexAndLength(1);
  return getOperation()->getOpOperand(range.first);
}

::mlir::MutableOperandRange AsyncCopyGlobalToLocalOp::getMaskMutable() {
  auto range = getODSOperandIndexAndLength(2);
  auto mutableRange = ::mlir::MutableOperandRange(getOperation(), range.first, range.second, ::mlir::MutableOperandRange::OperandSegment(2u, {getOperandSegmentSizesAttrName(), ::mlir::DenseI32ArrayAttr::get(getContext(), getProperties().operandSegmentSizes)}));
  return mutableRange;
}

::mlir::MutableOperandRange AsyncCopyGlobalToLocalOp::getOtherMutable() {
  auto range = getODSOperandIndexAndLength(3);
  auto mutableRange = ::mlir::MutableOperandRange(getOperation(), range.first, range.second, ::mlir::MutableOperandRange::OperandSegment(3u, {getOperandSegmentSizesAttrName(), ::mlir::DenseI32ArrayAttr::get(getContext(), getProperties().operandSegmentSizes)}));
  return mutableRange;
}

std::pair<unsigned, unsigned> AsyncCopyGlobalToLocalOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range AsyncCopyGlobalToLocalOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::triton::gpu::AsyncTokenType> AsyncCopyGlobalToLocalOp::getToken() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::AsyncTokenType>>(*getODSResults(0).begin());
}

::mlir::LogicalResult AsyncCopyGlobalToLocalOp::setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  ::mlir::DictionaryAttr dict = ::llvm::dyn_cast<::mlir::DictionaryAttr>(attr);
  if (!dict) {
    emitError() << "expected DictionaryAttr to set properties";
    return ::mlir::failure();
  }

  {
    auto &propStorage = prop.cache;
       auto attr = dict.get("cache");
    if (attr || /*isRequired=*/true) {
      if (!attr) {
        emitError() << "expected key entry for cache in DictionaryAttr to set "
                   "Properties.";
        return ::mlir::failure();
      }
      auto convertedAttr = ::llvm::dyn_cast<std::remove_reference_t<decltype(propStorage)>>(attr);
      if (convertedAttr) {
        propStorage = convertedAttr;
      } else {
        emitError() << "Invalid attribute `cache` in property conversion: " << attr;
        return ::mlir::failure();
      }
    }
  }

  {
    auto &propStorage = prop.evict;
       auto attr = dict.get("evict");
    if (attr || /*isRequired=*/true) {
      if (!attr) {
        emitError() << "expected key entry for evict in DictionaryAttr to set "
                   "Properties.";
        return ::mlir::failure();
      }
      auto convertedAttr = ::llvm::dyn_cast<std::remove_reference_t<decltype(propStorage)>>(attr);
      if (convertedAttr) {
        propStorage = convertedAttr;
      } else {
        emitError() << "Invalid attribute `evict` in property conversion: " << attr;
        return ::mlir::failure();
      }
    }
  }

  {
    auto &propStorage = prop.isVolatile;
       auto attr = dict.get("isVolatile");
    if (attr || /*isRequired=*/true) {
      if (!attr) {
        emitError() << "expected key entry for isVolatile in DictionaryAttr to set "
                   "Properties.";
        return ::mlir::failure();
      }
      auto convertedAttr = ::llvm::dyn_cast<std::remove_reference_t<decltype(propStorage)>>(attr);
      if (convertedAttr) {
        propStorage = convertedAttr;
      } else {
        emitError() << "Invalid attribute `isVolatile` in property conversion: " << attr;
        return ::mlir::failure();
      }
    }
  }
;
    {
      auto setFromAttr = [] (auto &propStorage, ::mlir::Attribute propAttr,
               ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
        return convertFromAttribute(propStorage, propAttr, emitError);;
      };
         auto attr = dict.get("operandSegmentSizes");   if (!attr) attr = dict.get("operand_segment_sizes");;
      if (!attr) {
        emitError() << "expected key entry for operandSegmentSizes in DictionaryAttr to set "
                   "Properties.";
        return ::mlir::failure();
      }
      if (::mlir::failed(setFromAttr(prop.operandSegmentSizes, attr, emitError)))
        return ::mlir::failure();
    }
  return ::mlir::success();
}

::mlir::Attribute AsyncCopyGlobalToLocalOp::getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop) {
    ::mlir::SmallVector<::mlir::NamedAttribute> attrs;
    ::mlir::Builder odsBuilder{ctx};

    {
      const auto &propStorage = prop.cache;
      if (propStorage)
        attrs.push_back(odsBuilder.getNamedAttr("cache",
                                       propStorage));
    }

    {
      const auto &propStorage = prop.evict;
      if (propStorage)
        attrs.push_back(odsBuilder.getNamedAttr("evict",
                                       propStorage));
    }

    {
      const auto &propStorage = prop.isVolatile;
      if (propStorage)
        attrs.push_back(odsBuilder.getNamedAttr("isVolatile",
                                       propStorage));
    }

    {
      const auto &propStorage = prop.operandSegmentSizes;
      attrs.push_back(odsBuilder.getNamedAttr("operandSegmentSizes",
                                              ::mlir::DenseI32ArrayAttr::get(ctx, propStorage)));
    }

  if (!attrs.empty())
    return odsBuilder.getDictionaryAttr(attrs);
  return {};
}

llvm::hash_code AsyncCopyGlobalToLocalOp::computePropertiesHash(const Properties &prop) {
  auto hash_operandSegmentSizes = [] (const auto &propStorage) -> llvm::hash_code {
    return ::llvm::hash_combine_range(std::begin(propStorage), std::end(propStorage));;
  };
  return llvm::hash_combine(
    llvm::hash_value(prop.cache.getAsOpaquePointer()), 
    llvm::hash_value(prop.evict.getAsOpaquePointer()), 
    llvm::hash_value(prop.isVolatile.getAsOpaquePointer()), 
    hash_operandSegmentSizes(prop.operandSegmentSizes));
}

std::optional<mlir::Attribute> AsyncCopyGlobalToLocalOp::getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name) {
    if (name == "cache")
      return prop.cache;

    if (name == "evict")
      return prop.evict;

    if (name == "isVolatile")
      return prop.isVolatile;
    if (name == "operand_segment_sizes" || name == "operandSegmentSizes") return ::mlir::DenseI32ArrayAttr::get(ctx, prop.operandSegmentSizes);
  return std::nullopt;
}

void AsyncCopyGlobalToLocalOp::setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value) {
    if (name == "cache") {
       prop.cache = ::llvm::dyn_cast_or_null<std::remove_reference_t<decltype(prop.cache)>>(value);
       return;
    }

    if (name == "evict") {
       prop.evict = ::llvm::dyn_cast_or_null<std::remove_reference_t<decltype(prop.evict)>>(value);
       return;
    }

    if (name == "isVolatile") {
       prop.isVolatile = ::llvm::dyn_cast_or_null<std::remove_reference_t<decltype(prop.isVolatile)>>(value);
       return;
    }
        if (name == "operand_segment_sizes" || name == "operandSegmentSizes") {
       auto arrAttr = ::llvm::dyn_cast_or_null<::mlir::DenseI32ArrayAttr>(value);
       if (!arrAttr) return;
       if (arrAttr.size() != sizeof(prop.operandSegmentSizes) / sizeof(int32_t))
         return;
       llvm::copy(arrAttr.asArrayRef(), prop.operandSegmentSizes.begin());
       return;
    }
}

void AsyncCopyGlobalToLocalOp::populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs) {
    if (prop.cache) attrs.append("cache", prop.cache);

    if (prop.evict) attrs.append("evict", prop.evict);

    if (prop.isVolatile) attrs.append("isVolatile", prop.isVolatile);
  attrs.append("operandSegmentSizes", ::mlir::DenseI32ArrayAttr::get(ctx, prop.operandSegmentSizes));
}

::mlir::LogicalResult AsyncCopyGlobalToLocalOp::verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
    {
      ::mlir::Attribute attr = attrs.get(getCacheAttrName(opName));
      if (attr && ::mlir::failed(__mlir_ods_local_attr_constraint_TritonGPUOps1(attr, "cache", emitError)))
        return ::mlir::failure();
    }

    {
      ::mlir::Attribute attr = attrs.get(getEvictAttrName(opName));
      if (attr && ::mlir::failed(__mlir_ods_local_attr_constraint_TritonGPUOps2(attr, "evict", emitError)))
        return ::mlir::failure();
    }

    {
      ::mlir::Attribute attr = attrs.get(getIsVolatileAttrName(opName));
      if (attr && ::mlir::failed(__mlir_ods_local_attr_constraint_TritonGPUOps3(attr, "isVolatile", emitError)))
        return ::mlir::failure();
    }
    return ::mlir::success();
}

::mlir::LogicalResult AsyncCopyGlobalToLocalOp::readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state) {
  auto &prop = state.getOrAddProperties<Properties>(); (void)prop;
  if (::mlir::failed(reader.readAttribute(prop.cache)))
    return ::mlir::failure();

  if (::mlir::failed(reader.readAttribute(prop.evict)))
    return ::mlir::failure();

  if (::mlir::failed(reader.readAttribute(prop.isVolatile)))
    return ::mlir::failure();

  if (reader.getBytecodeVersion() < /*kNativePropertiesODSSegmentSize=*/6) {
    auto &propStorage = prop.operandSegmentSizes;
    ::mlir::DenseI32ArrayAttr attr;
    if (::mlir::failed(reader.readAttribute(attr))) return ::mlir::failure();
    if (attr.size() > static_cast<int64_t>(sizeof(propStorage) / sizeof(int32_t))) {
      reader.emitError("size mismatch for operand/result_segment_size");
      return ::mlir::failure();
    }
    ::llvm::copy(::llvm::ArrayRef<int32_t>(attr), propStorage.begin());
  }

  {
    auto &propStorage = prop.operandSegmentSizes;
    auto readProp = [&]() {

  if (reader.getBytecodeVersion() >= /*kNativePropertiesODSSegmentSize=*/6)
    return reader.readSparseArray(::llvm::MutableArrayRef(propStorage));
;
      return ::mlir::success();
    };
    if (::mlir::failed(readProp()))
      return ::mlir::failure();
  }
  return ::mlir::success();
}

void AsyncCopyGlobalToLocalOp::writeProperties(::mlir::DialectBytecodeWriter &writer) {
  auto &prop = getProperties(); (void)prop;
  writer.writeAttribute(prop.cache);
  writer.writeAttribute(prop.evict);
  writer.writeAttribute(prop.isVolatile);

if (writer.getBytecodeVersion() < /*kNativePropertiesODSSegmentSize=*/6) {
  auto &propStorage = prop.operandSegmentSizes;
  writer.writeAttribute(::mlir::DenseI32ArrayAttr::get(this->getContext(), propStorage));
}

  {
    auto &propStorage = prop.operandSegmentSizes;

  if (writer.getBytecodeVersion() >= /*kNativePropertiesODSSegmentSize=*/6)
    writer.writeSparseArray(::llvm::ArrayRef(propStorage));
;
  }
}

::mlir::triton::CacheModifierAttr AsyncCopyGlobalToLocalOp::getCacheAttr() {
  return ::llvm::cast<::mlir::triton::CacheModifierAttr>(getProperties().cache);
}

::mlir::triton::CacheModifier AsyncCopyGlobalToLocalOp::getCache() {
  auto attr = getCacheAttr();
  return attr.getValue();
}

::mlir::triton::EvictionPolicyAttr AsyncCopyGlobalToLocalOp::getEvictAttr() {
  return ::llvm::cast<::mlir::triton::EvictionPolicyAttr>(getProperties().evict);
}

::mlir::triton::EvictionPolicy AsyncCopyGlobalToLocalOp::getEvict() {
  auto attr = getEvictAttr();
  return attr.getValue();
}

::mlir::BoolAttr AsyncCopyGlobalToLocalOp::getIsVolatileAttr() {
  return ::llvm::cast<::mlir::BoolAttr>(getProperties().isVolatile);
}

bool AsyncCopyGlobalToLocalOp::getIsVolatile() {
  auto attr = getIsVolatileAttr();
  return attr.getValue();
}

void AsyncCopyGlobalToLocalOp::setCacheAttr(::mlir::triton::CacheModifierAttr attr) {
  getProperties().cache = attr;
}

void AsyncCopyGlobalToLocalOp::setCache(::mlir::triton::CacheModifier attrValue) {
  getProperties().cache = ::mlir::triton::CacheModifierAttr::get(::mlir::Builder((*this)->getContext()).getContext(), attrValue);
}

void AsyncCopyGlobalToLocalOp::setEvictAttr(::mlir::triton::EvictionPolicyAttr attr) {
  getProperties().evict = attr;
}

void AsyncCopyGlobalToLocalOp::setEvict(::mlir::triton::EvictionPolicy attrValue) {
  getProperties().evict = ::mlir::triton::EvictionPolicyAttr::get(::mlir::Builder((*this)->getContext()).getContext(), attrValue);
}

void AsyncCopyGlobalToLocalOp::setIsVolatileAttr(::mlir::BoolAttr attr) {
  getProperties().isVolatile = attr;
}

void AsyncCopyGlobalToLocalOp::setIsVolatile(bool attrValue) {
  getProperties().isVolatile = ::mlir::Builder((*this)->getContext()).getBoolAttr(attrValue);
}

void AsyncCopyGlobalToLocalOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type token, ::mlir::Value src, ::mlir::Value dst, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, ::mlir::triton::CacheModifierAttr cache, ::mlir::triton::EvictionPolicyAttr evict, ::mlir::BoolAttr isVolatile) {
  odsState.addOperands(src);
  odsState.addOperands(dst);
  if (mask)
    odsState.addOperands(mask);
  if (other)
    odsState.addOperands(other);
  ::llvm::copy(::llvm::ArrayRef<int32_t>({1, 1, (mask ? 1 : 0), (other ? 1 : 0)}), odsState.getOrAddProperties<Properties>().operandSegmentSizes.begin());
  odsState.getOrAddProperties<Properties>().cache = cache;
  odsState.getOrAddProperties<Properties>().evict = evict;
  odsState.getOrAddProperties<Properties>().isVolatile = isVolatile;
  odsState.addTypes(token);
}

void AsyncCopyGlobalToLocalOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value src, ::mlir::Value dst, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, ::mlir::triton::CacheModifierAttr cache, ::mlir::triton::EvictionPolicyAttr evict, ::mlir::BoolAttr isVolatile) {
  odsState.addOperands(src);
  odsState.addOperands(dst);
  if (mask)
    odsState.addOperands(mask);
  if (other)
    odsState.addOperands(other);
  ::llvm::copy(::llvm::ArrayRef<int32_t>({1, 1, (mask ? 1 : 0), (other ? 1 : 0)}), odsState.getOrAddProperties<Properties>().operandSegmentSizes.begin());
  odsState.getOrAddProperties<Properties>().cache = cache;
  odsState.getOrAddProperties<Properties>().evict = evict;
  odsState.getOrAddProperties<Properties>().isVolatile = isVolatile;

        ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
        if (::mlir::succeeded(AsyncCopyGlobalToLocalOp::inferReturnTypes(odsBuilder.getContext(),
                      odsState.location, odsState.operands,
                      odsState.attributes.getDictionary(odsState.getContext()),
                      odsState.getRawProperties(),
                      odsState.regions, inferredReturnTypes)))
          odsState.addTypes(inferredReturnTypes);
        else
          ::llvm::report_fatal_error("Failed to infer result type(s).");
}

void AsyncCopyGlobalToLocalOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value dst, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, ::mlir::triton::CacheModifierAttr cache, ::mlir::triton::EvictionPolicyAttr evict, ::mlir::BoolAttr isVolatile) {
  odsState.addOperands(src);
  odsState.addOperands(dst);
  if (mask)
    odsState.addOperands(mask);
  if (other)
    odsState.addOperands(other);
  ::llvm::copy(::llvm::ArrayRef<int32_t>({1, 1, (mask ? 1 : 0), (other ? 1 : 0)}), odsState.getOrAddProperties<Properties>().operandSegmentSizes.begin());
  odsState.getOrAddProperties<Properties>().cache = cache;
  odsState.getOrAddProperties<Properties>().evict = evict;
  odsState.getOrAddProperties<Properties>().isVolatile = isVolatile;
  assert(resultTypes.size() == 1u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void AsyncCopyGlobalToLocalOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type token, ::mlir::Value src, ::mlir::Value dst, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, ::mlir::triton::CacheModifier cache, ::mlir::triton::EvictionPolicy evict, bool isVolatile) {
  odsState.addOperands(src);
  odsState.addOperands(dst);
  if (mask)
    odsState.addOperands(mask);
  if (other)
    odsState.addOperands(other);
  ::llvm::copy(::llvm::ArrayRef<int32_t>({1, 1, (mask ? 1 : 0), (other ? 1 : 0)}), odsState.getOrAddProperties<Properties>().operandSegmentSizes.begin());
  odsState.getOrAddProperties<Properties>().cache = ::mlir::triton::CacheModifierAttr::get(odsBuilder.getContext(), cache);
  odsState.getOrAddProperties<Properties>().evict = ::mlir::triton::EvictionPolicyAttr::get(odsBuilder.getContext(), evict);
  odsState.getOrAddProperties<Properties>().isVolatile = odsBuilder.getBoolAttr(isVolatile);
  odsState.addTypes(token);
}

void AsyncCopyGlobalToLocalOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value src, ::mlir::Value dst, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, ::mlir::triton::CacheModifier cache, ::mlir::triton::EvictionPolicy evict, bool isVolatile) {
  odsState.addOperands(src);
  odsState.addOperands(dst);
  if (mask)
    odsState.addOperands(mask);
  if (other)
    odsState.addOperands(other);
  ::llvm::copy(::llvm::ArrayRef<int32_t>({1, 1, (mask ? 1 : 0), (other ? 1 : 0)}), odsState.getOrAddProperties<Properties>().operandSegmentSizes.begin());
  odsState.getOrAddProperties<Properties>().cache = ::mlir::triton::CacheModifierAttr::get(odsBuilder.getContext(), cache);
  odsState.getOrAddProperties<Properties>().evict = ::mlir::triton::EvictionPolicyAttr::get(odsBuilder.getContext(), evict);
  odsState.getOrAddProperties<Properties>().isVolatile = odsBuilder.getBoolAttr(isVolatile);

        ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
        if (::mlir::succeeded(AsyncCopyGlobalToLocalOp::inferReturnTypes(odsBuilder.getContext(),
                      odsState.location, odsState.operands,
                      odsState.attributes.getDictionary(odsState.getContext()),
                      odsState.getRawProperties(),
                      odsState.regions, inferredReturnTypes)))
          odsState.addTypes(inferredReturnTypes);
        else
          ::llvm::report_fatal_error("Failed to infer result type(s).");
}

void AsyncCopyGlobalToLocalOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value dst, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, ::mlir::triton::CacheModifier cache, ::mlir::triton::EvictionPolicy evict, bool isVolatile) {
  odsState.addOperands(src);
  odsState.addOperands(dst);
  if (mask)
    odsState.addOperands(mask);
  if (other)
    odsState.addOperands(other);
  ::llvm::copy(::llvm::ArrayRef<int32_t>({1, 1, (mask ? 1 : 0), (other ? 1 : 0)}), odsState.getOrAddProperties<Properties>().operandSegmentSizes.begin());
  odsState.getOrAddProperties<Properties>().cache = ::mlir::triton::CacheModifierAttr::get(odsBuilder.getContext(), cache);
  odsState.getOrAddProperties<Properties>().evict = ::mlir::triton::EvictionPolicyAttr::get(odsBuilder.getContext(), evict);
  odsState.getOrAddProperties<Properties>().isVolatile = odsBuilder.getBoolAttr(isVolatile);
  assert(resultTypes.size() == 1u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void AsyncCopyGlobalToLocalOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() >= 2u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 1u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

void AsyncCopyGlobalToLocalOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() >= 2u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);

  ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
  if (::mlir::succeeded(AsyncCopyGlobalToLocalOp::inferReturnTypes(odsBuilder.getContext(),
          odsState.location, operands,
          odsState.attributes.getDictionary(odsState.getContext()),
          odsState.getRawProperties(),
          odsState.regions, inferredReturnTypes))) {
    assert(inferredReturnTypes.size() == 1u && "mismatched number of return types");
    odsState.addTypes(inferredReturnTypes);
  } else {
    ::llvm::report_fatal_error("Failed to infer result type(s).");
  }
}

::mlir::LogicalResult AsyncCopyGlobalToLocalOp::verifyInvariantsImpl() {
  auto tblgen_cache = getProperties().cache; (void)tblgen_cache;
  if (!tblgen_cache) return emitOpError("requires attribute 'cache'");
  auto tblgen_evict = getProperties().evict; (void)tblgen_evict;
  if (!tblgen_evict) return emitOpError("requires attribute 'evict'");
  auto tblgen_isVolatile = getProperties().isVolatile; (void)tblgen_isVolatile;
  if (!tblgen_isVolatile) return emitOpError("requires attribute 'isVolatile'");

  if (::mlir::failed(__mlir_ods_local_attr_constraint_TritonGPUOps1(*this, tblgen_cache, "cache")))
    return ::mlir::failure();

  if (::mlir::failed(__mlir_ods_local_attr_constraint_TritonGPUOps2(*this, tblgen_evict, "evict")))
    return ::mlir::failure();

  if (::mlir::failed(__mlir_ods_local_attr_constraint_TritonGPUOps3(*this, tblgen_isVolatile, "isVolatile")))
    return ::mlir::failure();
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSOperands(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps2(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
    auto valueGroup1 = getODSOperands(1);

    for (auto v : valueGroup1) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps3(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
    auto valueGroup2 = getODSOperands(2);

    if (valueGroup2.size() > 1) {
      return emitOpError("operand group starting at #") << index
          << " requires 0 or 1 element, but found " << valueGroup2.size();
    }

    for (auto v : valueGroup2) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps4(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
    auto valueGroup3 = getODSOperands(3);

    if (valueGroup3.size() > 1) {
      return emitOpError("operand group starting at #") << index
          << " requires 0 or 1 element, but found " << valueGroup3.size();
    }

    for (auto v : valueGroup3) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps5(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
  }
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSResults(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps1(*this, v.getType(), "result", index++)))
        return ::mlir::failure();
    }
  }
  if (!((((*this->getOperation()).getOperands().size() <= 3) || std::equal_to<>()(getI1SameShape((*this->getODSOperands(0).begin()).getType()), (*this->getODSOperands(2).begin()).getType()))))
    return emitOpError("failed to verify that infer mask type from src type");
  if (!((((*this->getOperation()).getOperands().size() <= 4) || std::equal_to<>()(getPointeeType((*this->getODSOperands(0).begin()).getType()), (*this->getODSOperands(3).begin()).getType()))))
    return emitOpError("failed to verify that infer other type from src type");
  return ::mlir::success();
}

::mlir::LogicalResult AsyncCopyGlobalToLocalOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::LogicalResult AsyncCopyGlobalToLocalOp::inferReturnTypes(::mlir::MLIRContext *context, ::std::optional<::mlir::Location> location, ::mlir::ValueRange operands, ::mlir::DictionaryAttr attributes, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions, ::llvm::SmallVectorImpl<::mlir::Type>&inferredReturnTypes) {
  inferredReturnTypes.resize(1);
  ::mlir::Builder odsBuilder(context);
  ::mlir::Type odsInferredType0 = odsBuilder.getType<::mlir::triton::gpu::AsyncTokenType>();
  inferredReturnTypes[0] = odsInferredType0;
  return ::mlir::success();
}

::mlir::ParseResult AsyncCopyGlobalToLocalOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::mlir::OpAsmParser::UnresolvedOperand srcRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> srcOperands(srcRawOperands);  ::llvm::SMLoc srcOperandsLoc;
  (void)srcOperandsLoc;
  ::mlir::OpAsmParser::UnresolvedOperand dstRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> dstOperands(dstRawOperands);  ::llvm::SMLoc dstOperandsLoc;
  (void)dstOperandsLoc;
  ::llvm::SmallVector<::mlir::OpAsmParser::UnresolvedOperand, 4> maskOperands;
  ::llvm::SMLoc maskOperandsLoc;
  (void)maskOperandsLoc;
  ::llvm::SmallVector<::mlir::OpAsmParser::UnresolvedOperand, 4> otherOperands;
  ::llvm::SMLoc otherOperandsLoc;
  (void)otherOperandsLoc;
  ::mlir::Type srcRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> srcTypes(srcRawTypes);
  ::mlir::Type dstRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> dstTypes(dstRawTypes);

  srcOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperand(srcRawOperands[0]))
    return ::mlir::failure();
  if (parser.parseComma())
    return ::mlir::failure();

  dstOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperand(dstRawOperands[0]))
    return ::mlir::failure();
  if (::mlir::succeeded(parser.parseOptionalKeyword("mask"))) {

  {
    maskOperandsLoc = parser.getCurrentLocation();
    ::mlir::OpAsmParser::UnresolvedOperand operand;
    ::mlir::OptionalParseResult parseResult =
                                    parser.parseOptionalOperand(operand);
    if (parseResult.has_value()) {
      if (failed(*parseResult))
        return ::mlir::failure();
      maskOperands.push_back(operand);
    }
  }
  }
  if (::mlir::succeeded(parser.parseOptionalKeyword("other"))) {

  {
    otherOperandsLoc = parser.getCurrentLocation();
    ::mlir::OpAsmParser::UnresolvedOperand operand;
    ::mlir::OptionalParseResult parseResult =
                                    parser.parseOptionalOperand(operand);
    if (parseResult.has_value()) {
      if (failed(*parseResult))
        return ::mlir::failure();
      otherOperands.push_back(operand);
    }
  }
  }
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
    if (failed(verifyInherentAttrs(result.name, result.attributes, [&]() {
        return parser.emitError(loc) << "'" << result.name.getStringRef() << "' op ";
      })))
      return ::mlir::failure();
  }
  if (parser.parseColon())
    return ::mlir::failure();

  {
    ::mlir::RankedTensorType type;
    if (parser.parseCustomTypeWithFallback(type))
      return ::mlir::failure();
    srcRawTypes[0] = type;
  }
  if (parser.parseArrow())
    return ::mlir::failure();

  {
    ::mlir::triton::MemDescType type;
    if (parser.parseCustomTypeWithFallback(type))
      return ::mlir::failure();
    dstRawTypes[0] = type;
  }
::llvm::copy(::llvm::ArrayRef<int32_t>({1, 1, static_cast<int32_t>(maskOperands.size()), static_cast<int32_t>(otherOperands.size())}), result.getOrAddProperties<AsyncCopyGlobalToLocalOp::Properties>().operandSegmentSizes.begin());
  for (::mlir::Type type : srcTypes) {
    (void)type;
    if (!(((::llvm::isa<::mlir::RankedTensorType>(type))) && ([](::mlir::Type elementType) { return ((elementType.isa<::mlir::triton::PointerType>())) && ([](::mlir::Type pointeeType) { return (true); }(elementType.cast<::mlir::triton::PointerType>().getPointeeType())); }(::llvm::cast<::mlir::ShapedType>(type).getElementType())))) {
      return parser.emitError(parser.getNameLoc()) << "'src' must be ranked tensor of ptr values, but got " << type;
    }
  }
  ::mlir::Type odsBuildableType0 = parser.getBuilder().getType<::mlir::triton::gpu::AsyncTokenType>();
  result.addTypes(odsBuildableType0);
  if (parser.resolveOperands(srcOperands, srcTypes, srcOperandsLoc, result.operands))
    return ::mlir::failure();
  if (parser.resolveOperands(dstOperands, dstTypes, dstOperandsLoc, result.operands))
    return ::mlir::failure();
  if (parser.resolveOperands(maskOperands, getI1SameShape(srcTypes[0]), maskOperandsLoc, result.operands))
    return ::mlir::failure();
  if (parser.resolveOperands(otherOperands, getPointeeType(srcTypes[0]), otherOperandsLoc, result.operands))
    return ::mlir::failure();
  return ::mlir::success();
}

void AsyncCopyGlobalToLocalOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  _odsPrinter << ' ';
  _odsPrinter << getSrc();
  _odsPrinter << ",";
  _odsPrinter << ' ';
  _odsPrinter << getDst();
  if (getMask()) {
    _odsPrinter << ' ' << "mask";
    _odsPrinter << ' ';
    if (::mlir::Value value = getMask())
      _odsPrinter << value;
  }
  if (getOther()) {
    _odsPrinter << ' ' << "other";
    _odsPrinter << ' ';
    if (::mlir::Value value = getOther())
      _odsPrinter << value;
  }
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  elidedAttrs.push_back("operandSegmentSizes");
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
  _odsPrinter << ' ' << ":";
  _odsPrinter << ' ';
  {
    auto type = getSrc().getType();
    if (auto validType = ::llvm::dyn_cast<::mlir::RankedTensorType>(type))
      _odsPrinter.printStrippedAttrOrType(validType);
   else
     _odsPrinter << type;
  }
  _odsPrinter << ' ' << "->";
  _odsPrinter << ' ';
  {
    auto type = getDst().getType();
    if (auto validType = ::llvm::dyn_cast<::mlir::triton::MemDescType>(type))
      _odsPrinter.printStrippedAttrOrType(validType);
   else
     _odsPrinter << type;
  }
}

void AsyncCopyGlobalToLocalOp::getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects) {
  effects.emplace_back(::mlir::MemoryEffects::Read::get(), 0, false, ::mlir::triton::GlobalMemory::get());
  effects.emplace_back(::mlir::MemoryEffects::Write::get(), 0, false, ::mlir::triton::gpu::SharedMemory::get());
}

} // namespace gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::gpu::AsyncCopyGlobalToLocalOp)

namespace mlir {
namespace triton {
namespace gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::gpu::AsyncWaitOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
AsyncWaitOpGenericAdaptorBase::AsyncWaitOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_gpu.async_wait", odsAttrs.getContext());
}

AsyncWaitOpGenericAdaptorBase::AsyncWaitOpGenericAdaptorBase(AsyncWaitOp op) : AsyncWaitOpGenericAdaptorBase(op->getDiscardableAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> AsyncWaitOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  bool isVariadic[] = {true};
  int prevVariadicCount = 0;
  for (unsigned i = 0; i < index; ++i)
    if (isVariadic[i]) ++prevVariadicCount;

  // Calculate how many dynamic values a static variadic operand corresponds to.
  // This assumes all static variadic operands have the same dynamic value count.
  int variadicSize = (odsOperandsSize - 0) / 1;
  // `index` passed in as the parameter is the static index which counts each
  // operand (variadic or not) as size 1. So here for each previous static variadic
  // operand, we need to offset by (variadicSize - 1) to get where the dynamic
  // value pack for this static operand starts.
  int start = index + (variadicSize - 1) * prevVariadicCount;
  int size = isVariadic[index] ? variadicSize : 1;
  return {start, size};
}

::mlir::DictionaryAttr AsyncWaitOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

::mlir::IntegerAttr AsyncWaitOpGenericAdaptorBase::getNumAttr() {
  auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().num);
  return attr;
}

uint32_t AsyncWaitOpGenericAdaptorBase::getNum() {
  auto attr = getNumAttr();
  return attr.getValue().getZExtValue();
}

} // namespace detail
AsyncWaitOpAdaptor::AsyncWaitOpAdaptor(AsyncWaitOp op) : AsyncWaitOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult AsyncWaitOpAdaptor::verify(::mlir::Location loc) {
  auto tblgen_num = getProperties().num; (void)tblgen_num;
  if (!tblgen_num) return emitError(loc, "'triton_gpu.async_wait' op ""requires attribute 'num'");

  if (tblgen_num && !(((::llvm::isa<::mlir::IntegerAttr>(tblgen_num))) && ((::llvm::cast<::mlir::IntegerAttr>(tblgen_num).getType().isSignlessInteger(32)))))
    return emitError(loc, "'triton_gpu.async_wait' op ""attribute 'num' failed to satisfy constraint: 32-bit signless integer attribute");
  return ::mlir::success();
}

std::pair<unsigned, unsigned> AsyncWaitOp::getODSOperandIndexAndLength(unsigned index) {
  bool isVariadic[] = {true};
  int prevVariadicCount = 0;
  for (unsigned i = 0; i < index; ++i)
    if (isVariadic[i]) ++prevVariadicCount;

  // Calculate how many dynamic values a static variadic operand corresponds to.
  // This assumes all static variadic operands have the same dynamic value count.
  int variadicSize = (getOperation()->getNumOperands() - 0) / 1;
  // `index` passed in as the parameter is the static index which counts each
  // operand (variadic or not) as size 1. So here for each previous static variadic
  // operand, we need to offset by (variadicSize - 1) to get where the dynamic
  // value pack for this static operand starts.
  int start = index + (variadicSize - 1) * prevVariadicCount;
  int size = isVariadic[index] ? variadicSize : 1;
  return {start, size};
}

::mlir::Operation::operand_range AsyncWaitOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

::mlir::Operation::operand_range AsyncWaitOp::getAsyncToken() {
  return getODSOperands(0);
}

::mlir::MutableOperandRange AsyncWaitOp::getAsyncTokenMutable() {
  auto range = getODSOperandIndexAndLength(0);
  auto mutableRange = ::mlir::MutableOperandRange(getOperation(), range.first, range.second);
  return mutableRange;
}

std::pair<unsigned, unsigned> AsyncWaitOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range AsyncWaitOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::LogicalResult AsyncWaitOp::setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  ::mlir::DictionaryAttr dict = ::llvm::dyn_cast<::mlir::DictionaryAttr>(attr);
  if (!dict) {
    emitError() << "expected DictionaryAttr to set properties";
    return ::mlir::failure();
  }

  {
    auto &propStorage = prop.num;
       auto attr = dict.get("num");
    if (attr || /*isRequired=*/true) {
      if (!attr) {
        emitError() << "expected key entry for num in DictionaryAttr to set "
                   "Properties.";
        return ::mlir::failure();
      }
      auto convertedAttr = ::llvm::dyn_cast<std::remove_reference_t<decltype(propStorage)>>(attr);
      if (convertedAttr) {
        propStorage = convertedAttr;
      } else {
        emitError() << "Invalid attribute `num` in property conversion: " << attr;
        return ::mlir::failure();
      }
    }
  }
  return ::mlir::success();
}

::mlir::Attribute AsyncWaitOp::getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop) {
    ::mlir::SmallVector<::mlir::NamedAttribute> attrs;
    ::mlir::Builder odsBuilder{ctx};

    {
      const auto &propStorage = prop.num;
      if (propStorage)
        attrs.push_back(odsBuilder.getNamedAttr("num",
                                       propStorage));
    }

  if (!attrs.empty())
    return odsBuilder.getDictionaryAttr(attrs);
  return {};
}

llvm::hash_code AsyncWaitOp::computePropertiesHash(const Properties &prop) {
  return llvm::hash_combine(
    llvm::hash_value(prop.num.getAsOpaquePointer()));
}

std::optional<mlir::Attribute> AsyncWaitOp::getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name) {
    if (name == "num")
      return prop.num;
  return std::nullopt;
}

void AsyncWaitOp::setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value) {
    if (name == "num") {
       prop.num = ::llvm::dyn_cast_or_null<std::remove_reference_t<decltype(prop.num)>>(value);
       return;
    }
}

void AsyncWaitOp::populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs) {
    if (prop.num) attrs.append("num", prop.num);
}

::mlir::LogicalResult AsyncWaitOp::verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
    {
      ::mlir::Attribute attr = attrs.get(getNumAttrName(opName));
      if (attr && ::mlir::failed(__mlir_ods_local_attr_constraint_TritonGPUOps0(attr, "num", emitError)))
        return ::mlir::failure();
    }
    return ::mlir::success();
}

::mlir::LogicalResult AsyncWaitOp::readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state) {
  auto &prop = state.getOrAddProperties<Properties>(); (void)prop;
  if (::mlir::failed(reader.readAttribute(prop.num)))
    return ::mlir::failure();
  return ::mlir::success();
}

void AsyncWaitOp::writeProperties(::mlir::DialectBytecodeWriter &writer) {
  auto &prop = getProperties(); (void)prop;
  writer.writeAttribute(prop.num);
}

::mlir::IntegerAttr AsyncWaitOp::getNumAttr() {
  return ::llvm::cast<::mlir::IntegerAttr>(getProperties().num);
}

uint32_t AsyncWaitOp::getNum() {
  auto attr = getNumAttr();
  return attr.getValue().getZExtValue();
}

void AsyncWaitOp::setNumAttr(::mlir::IntegerAttr attr) {
  getProperties().num = attr;
}

void AsyncWaitOp::setNum(uint32_t attrValue) {
  getProperties().num = ::mlir::Builder((*this)->getContext()).getIntegerAttr(::mlir::Builder((*this)->getContext()).getIntegerType(32), attrValue);
}

void AsyncWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange asyncToken, ::mlir::IntegerAttr num) {
  odsState.addOperands(asyncToken);
  odsState.getOrAddProperties<Properties>().num = num;
}

void AsyncWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange asyncToken, ::mlir::IntegerAttr num) {
  odsState.addOperands(asyncToken);
  odsState.getOrAddProperties<Properties>().num = num;
  assert(resultTypes.size() == 0u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void AsyncWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange asyncToken, uint32_t num) {
  odsState.addOperands(asyncToken);
  odsState.getOrAddProperties<Properties>().num = odsBuilder.getIntegerAttr(odsBuilder.getIntegerType(32), num);
}

void AsyncWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange asyncToken, uint32_t num) {
  odsState.addOperands(asyncToken);
  odsState.getOrAddProperties<Properties>().num = odsBuilder.getIntegerAttr(odsBuilder.getIntegerType(32), num);
  assert(resultTypes.size() == 0u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void AsyncWaitOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 0u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

::mlir::LogicalResult AsyncWaitOp::verifyInvariantsImpl() {
  auto tblgen_num = getProperties().num; (void)tblgen_num;
  if (!tblgen_num) return emitOpError("requires attribute 'num'");

  if (::mlir::failed(__mlir_ods_local_attr_constraint_TritonGPUOps0(*this, tblgen_num, "num")))
    return ::mlir::failure();
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSOperands(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps0(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
  }
  return ::mlir::success();
}

::mlir::LogicalResult AsyncWaitOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult AsyncWaitOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::llvm::SmallVector<::mlir::OpAsmParser::UnresolvedOperand, 4> asyncTokenOperands;
  ::llvm::SMLoc asyncTokenOperandsLoc;
  (void)asyncTokenOperandsLoc;

  asyncTokenOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperandList(asyncTokenOperands))
    return ::mlir::failure();
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
    if (failed(verifyInherentAttrs(result.name, result.attributes, [&]() {
        return parser.emitError(loc) << "'" << result.name.getStringRef() << "' op ";
      })))
      return ::mlir::failure();
  }
  ::mlir::Type odsBuildableType0 = parser.getBuilder().getType<::mlir::triton::gpu::AsyncTokenType>();
  if (parser.resolveOperands(asyncTokenOperands, odsBuildableType0, asyncTokenOperandsLoc, result.operands))
    return ::mlir::failure();
  return ::mlir::success();
}

void AsyncWaitOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  _odsPrinter << ' ';
  _odsPrinter << getAsyncToken();
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
}

} // namespace gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::gpu::AsyncWaitOp)

namespace mlir {
namespace triton {
namespace gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::gpu::ConvertLayoutOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
ConvertLayoutOpGenericAdaptorBase::ConvertLayoutOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const ::mlir::EmptyProperties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_gpu.convert_layout", odsAttrs.getContext());
}

ConvertLayoutOpGenericAdaptorBase::ConvertLayoutOpGenericAdaptorBase(ConvertLayoutOp op) : ConvertLayoutOpGenericAdaptorBase(op->getAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> ConvertLayoutOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  return {index, 1};
}

::mlir::DictionaryAttr ConvertLayoutOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

} // namespace detail
ConvertLayoutOpAdaptor::ConvertLayoutOpAdaptor(ConvertLayoutOp op) : ConvertLayoutOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult ConvertLayoutOpAdaptor::verify(::mlir::Location loc) {
  return ::mlir::success();
}

std::pair<unsigned, unsigned> ConvertLayoutOp::getODSOperandIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::operand_range ConvertLayoutOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::RankedTensorType> ConvertLayoutOp::getSrc() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(0).begin());
}

::mlir::OpOperand &ConvertLayoutOp::getSrcMutable() {
  auto range = getODSOperandIndexAndLength(0);
  return getOperation()->getOpOperand(range.first);
}

std::pair<unsigned, unsigned> ConvertLayoutOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range ConvertLayoutOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::RankedTensorType> ConvertLayoutOp::getResult() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
}

void ConvertLayoutOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value src) {
  odsState.addOperands(src);
  odsState.addTypes(result);
}

void ConvertLayoutOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src) {
  odsState.addOperands(src);
  assert(resultTypes.size() == 1u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void ConvertLayoutOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 1u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 1u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

::mlir::LogicalResult ConvertLayoutOp::verifyInvariantsImpl() {
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSOperands(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps6(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
  }
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSResults(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps6(*this, v.getType(), "result", index++)))
        return ::mlir::failure();
    }
  }
  return ::mlir::success();
}

::mlir::LogicalResult ConvertLayoutOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult ConvertLayoutOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::mlir::OpAsmParser::UnresolvedOperand srcRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> srcOperands(srcRawOperands);  ::llvm::SMLoc srcOperandsLoc;
  (void)srcOperandsLoc;
  ::mlir::Type srcRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> srcTypes(srcRawTypes);
  ::mlir::Type resultRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> resultTypes(resultRawTypes);

  srcOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperand(srcRawOperands[0]))
    return ::mlir::failure();
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
  }
  if (parser.parseColon())
    return ::mlir::failure();

  {
    ::mlir::RankedTensorType type;
    if (parser.parseCustomTypeWithFallback(type))
      return ::mlir::failure();
    srcRawTypes[0] = type;
  }
  if (parser.parseArrow())
    return ::mlir::failure();

  {
    ::mlir::RankedTensorType type;
    if (parser.parseCustomTypeWithFallback(type))
      return ::mlir::failure();
    resultRawTypes[0] = type;
  }
  result.addTypes(resultTypes);
  if (parser.resolveOperands(srcOperands, srcTypes, srcOperandsLoc, result.operands))
    return ::mlir::failure();
  return ::mlir::success();
}

void ConvertLayoutOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  _odsPrinter << ' ';
  _odsPrinter << getSrc();
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
  _odsPrinter << ' ' << ":";
  _odsPrinter << ' ';
  {
    auto type = getSrc().getType();
    if (auto validType = ::llvm::dyn_cast<::mlir::RankedTensorType>(type))
      _odsPrinter.printStrippedAttrOrType(validType);
   else
     _odsPrinter << type;
  }
  _odsPrinter << ' ' << "->";
  _odsPrinter << ' ';
  {
    auto type = getResult().getType();
    if (auto validType = ::llvm::dyn_cast<::mlir::RankedTensorType>(type))
      _odsPrinter.printStrippedAttrOrType(validType);
   else
     _odsPrinter << type;
  }
}

void ConvertLayoutOp::getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects) {
}

} // namespace gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::gpu::ConvertLayoutOp)

namespace mlir {
namespace triton {
namespace gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::gpu::LocalAllocOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
LocalAllocOpGenericAdaptorBase::LocalAllocOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const ::mlir::EmptyProperties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_gpu.local_alloc", odsAttrs.getContext());
}

LocalAllocOpGenericAdaptorBase::LocalAllocOpGenericAdaptorBase(LocalAllocOp op) : LocalAllocOpGenericAdaptorBase(op->getAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> LocalAllocOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  bool isVariadic[] = {true};
  int prevVariadicCount = 0;
  for (unsigned i = 0; i < index; ++i)
    if (isVariadic[i]) ++prevVariadicCount;

  // Calculate how many dynamic values a static variadic operand corresponds to.
  // This assumes all static variadic operands have the same dynamic value count.
  int variadicSize = (odsOperandsSize - 0) / 1;
  // `index` passed in as the parameter is the static index which counts each
  // operand (variadic or not) as size 1. So here for each previous static variadic
  // operand, we need to offset by (variadicSize - 1) to get where the dynamic
  // value pack for this static operand starts.
  int start = index + (variadicSize - 1) * prevVariadicCount;
  int size = isVariadic[index] ? variadicSize : 1;
  return {start, size};
}

::mlir::DictionaryAttr LocalAllocOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

} // namespace detail
LocalAllocOpAdaptor::LocalAllocOpAdaptor(LocalAllocOp op) : LocalAllocOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult LocalAllocOpAdaptor::verify(::mlir::Location loc) {
  return ::mlir::success();
}

std::pair<unsigned, unsigned> LocalAllocOp::getODSOperandIndexAndLength(unsigned index) {
  bool isVariadic[] = {true};
  int prevVariadicCount = 0;
  for (unsigned i = 0; i < index; ++i)
    if (isVariadic[i]) ++prevVariadicCount;

  // Calculate how many dynamic values a static variadic operand corresponds to.
  // This assumes all static variadic operands have the same dynamic value count.
  int variadicSize = (getOperation()->getNumOperands() - 0) / 1;
  // `index` passed in as the parameter is the static index which counts each
  // operand (variadic or not) as size 1. So here for each previous static variadic
  // operand, we need to offset by (variadicSize - 1) to get where the dynamic
  // value pack for this static operand starts.
  int start = index + (variadicSize - 1) * prevVariadicCount;
  int size = isVariadic[index] ? variadicSize : 1;
  return {start, size};
}

::mlir::Operation::operand_range LocalAllocOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::RankedTensorType> LocalAllocOp::getInit() {
  auto operands = getODSOperands(0);
  return operands.empty() ? ::mlir::TypedValue<::mlir::RankedTensorType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*operands.begin());
}

::mlir::MutableOperandRange LocalAllocOp::getInitMutable() {
  auto range = getODSOperandIndexAndLength(0);
  auto mutableRange = ::mlir::MutableOperandRange(getOperation(), range.first, range.second);
  return mutableRange;
}

std::pair<unsigned, unsigned> LocalAllocOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range LocalAllocOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::triton::MemDescType> LocalAllocOp::getResult() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::triton::MemDescType>>(*getODSResults(0).begin());
}

void LocalAllocOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, /*optional*/::mlir::Value init) {
  if (init)
    odsState.addOperands(init);
  odsState.addTypes(result);
}

void LocalAllocOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, /*optional*/::mlir::Value init) {
  if (init)
    odsState.addOperands(init);
  assert(resultTypes.size() == 1u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void LocalAllocOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 1u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

::mlir::LogicalResult LocalAllocOp::verifyInvariantsImpl() {
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSOperands(0);

    if (valueGroup0.size() > 1) {
      return emitOpError("operand group starting at #") << index
          << " requires 0 or 1 element, but found " << valueGroup0.size();
    }

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps6(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
  }
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSResults(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps3(*this, v.getType(), "result", index++)))
        return ::mlir::failure();
    }
  }
  return ::mlir::success();
}

::mlir::LogicalResult LocalAllocOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult LocalAllocOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::llvm::SmallVector<::mlir::OpAsmParser::UnresolvedOperand, 4> initOperands;
  ::llvm::SMLoc initOperandsLoc;
  (void)initOperandsLoc;
  ::llvm::ArrayRef<::mlir::Type> allOperandTypes;
  ::llvm::ArrayRef<::mlir::Type> allResultTypes;

  {
    initOperandsLoc = parser.getCurrentLocation();
    ::mlir::OpAsmParser::UnresolvedOperand operand;
    ::mlir::OptionalParseResult parseResult =
                                    parser.parseOptionalOperand(operand);
    if (parseResult.has_value()) {
      if (failed(*parseResult))
        return ::mlir::failure();
      initOperands.push_back(operand);
    }
  }
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
  }
  if (parser.parseColon())
    return ::mlir::failure();

  ::mlir::FunctionType allOperand__allResult_functionType;
  if (parser.parseType(allOperand__allResult_functionType))
    return ::mlir::failure();
  allOperandTypes = allOperand__allResult_functionType.getInputs();
  allResultTypes = allOperand__allResult_functionType.getResults();
  result.addTypes(allResultTypes);
  if (parser.resolveOperands(initOperands, allOperandTypes, parser.getNameLoc(), result.operands))
    return ::mlir::failure();
  return ::mlir::success();
}

void LocalAllocOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  _odsPrinter << ' ';
  if (::mlir::Value value = getInit())
    _odsPrinter << value;
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
  _odsPrinter << ' ' << ":";
  _odsPrinter << ' ';
  _odsPrinter.printFunctionalType(getOperation()->getOperandTypes(), getOperation()->getResultTypes());
}

} // namespace gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::gpu::LocalAllocOp)

namespace mlir {
namespace triton {
namespace gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::gpu::LocalDeallocOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
LocalDeallocOpGenericAdaptorBase::LocalDeallocOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const ::mlir::EmptyProperties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_gpu.local_dealloc", odsAttrs.getContext());
}

LocalDeallocOpGenericAdaptorBase::LocalDeallocOpGenericAdaptorBase(LocalDeallocOp op) : LocalDeallocOpGenericAdaptorBase(op->getAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> LocalDeallocOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  return {index, 1};
}

::mlir::DictionaryAttr LocalDeallocOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

} // namespace detail
LocalDeallocOpAdaptor::LocalDeallocOpAdaptor(LocalDeallocOp op) : LocalDeallocOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult LocalDeallocOpAdaptor::verify(::mlir::Location loc) {
  return ::mlir::success();
}

std::pair<unsigned, unsigned> LocalDeallocOp::getODSOperandIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::operand_range LocalDeallocOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::triton::MemDescType> LocalDeallocOp::getPtr() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::triton::MemDescType>>(*getODSOperands(0).begin());
}

::mlir::OpOperand &LocalDeallocOp::getPtrMutable() {
  auto range = getODSOperandIndexAndLength(0);
  return getOperation()->getOpOperand(range.first);
}

std::pair<unsigned, unsigned> LocalDeallocOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range LocalDeallocOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

void LocalDeallocOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value ptr) {
  odsState.addOperands(ptr);
}

void LocalDeallocOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr) {
  odsState.addOperands(ptr);
  assert(resultTypes.size() == 0u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void LocalDeallocOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 1u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 0u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

::mlir::LogicalResult LocalDeallocOp::verifyInvariantsImpl() {
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSOperands(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps3(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
  }
  return ::mlir::success();
}

::mlir::LogicalResult LocalDeallocOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult LocalDeallocOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::mlir::OpAsmParser::UnresolvedOperand ptrRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> ptrOperands(ptrRawOperands);  ::llvm::SMLoc ptrOperandsLoc;
  (void)ptrOperandsLoc;
  ::mlir::Type ptrRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> ptrTypes(ptrRawTypes);

  ptrOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperand(ptrRawOperands[0]))
    return ::mlir::failure();
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
  }
  if (parser.parseColon())
    return ::mlir::failure();

  if (parser.parseType(ptrRawTypes[0]))
    return ::mlir::failure();
  if (parser.resolveOperands(ptrOperands, ptrTypes, ptrOperandsLoc, result.operands))
    return ::mlir::failure();
  return ::mlir::success();
}

void LocalDeallocOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  _odsPrinter << ' ';
  _odsPrinter << getPtr();
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
  _odsPrinter << ' ' << ":";
  _odsPrinter << ' ';
   _odsPrinter << getPtr().getType();
}

void LocalDeallocOp::getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects) {
  effects.emplace_back(::mlir::MemoryEffects::Free::get(), 0, false, ::mlir::triton::gpu::SharedMemory::get());
}

} // namespace gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::gpu::LocalDeallocOp)

namespace mlir {
namespace triton {
namespace gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::gpu::LocalLoadOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
LocalLoadOpGenericAdaptorBase::LocalLoadOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const ::mlir::EmptyProperties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_gpu.local_load", odsAttrs.getContext());
}

LocalLoadOpGenericAdaptorBase::LocalLoadOpGenericAdaptorBase(LocalLoadOp op) : LocalLoadOpGenericAdaptorBase(op->getAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> LocalLoadOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  return {index, 1};
}

::mlir::DictionaryAttr LocalLoadOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

} // namespace detail
LocalLoadOpAdaptor::LocalLoadOpAdaptor(LocalLoadOp op) : LocalLoadOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult LocalLoadOpAdaptor::verify(::mlir::Location loc) {
  return ::mlir::success();
}

std::pair<unsigned, unsigned> LocalLoadOp::getODSOperandIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::operand_range LocalLoadOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::triton::MemDescType> LocalLoadOp::getSrc() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::triton::MemDescType>>(*getODSOperands(0).begin());
}

::mlir::OpOperand &LocalLoadOp::getSrcMutable() {
  auto range = getODSOperandIndexAndLength(0);
  return getOperation()->getOpOperand(range.first);
}

std::pair<unsigned, unsigned> LocalLoadOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range LocalLoadOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::RankedTensorType> LocalLoadOp::getResult() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
}

void LocalLoadOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value src) {
  odsState.addOperands(src);
  odsState.addTypes(result);
}

void LocalLoadOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src) {
  odsState.addOperands(src);
  assert(resultTypes.size() == 1u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void LocalLoadOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 1u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 1u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

::mlir::LogicalResult LocalLoadOp::verifyInvariantsImpl() {
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSOperands(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps3(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
  }
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSResults(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps6(*this, v.getType(), "result", index++)))
        return ::mlir::failure();
    }
  }
  return ::mlir::success();
}

::mlir::LogicalResult LocalLoadOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult LocalLoadOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::mlir::OpAsmParser::UnresolvedOperand srcRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> srcOperands(srcRawOperands);  ::llvm::SMLoc srcOperandsLoc;
  (void)srcOperandsLoc;
  ::mlir::Type srcRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> srcTypes(srcRawTypes);
  ::mlir::Type resultRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> resultTypes(resultRawTypes);

  srcOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperand(srcRawOperands[0]))
    return ::mlir::failure();
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
  }
  if (parser.parseColon())
    return ::mlir::failure();

  if (parser.parseType(srcRawTypes[0]))
    return ::mlir::failure();
  if (parser.parseArrow())
    return ::mlir::failure();

  {
    ::mlir::RankedTensorType type;
    if (parser.parseCustomTypeWithFallback(type))
      return ::mlir::failure();
    resultRawTypes[0] = type;
  }
  result.addTypes(resultTypes);
  if (parser.resolveOperands(srcOperands, srcTypes, srcOperandsLoc, result.operands))
    return ::mlir::failure();
  return ::mlir::success();
}

void LocalLoadOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  _odsPrinter << ' ';
  _odsPrinter << getSrc();
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
  _odsPrinter << ' ' << ":";
  _odsPrinter << ' ';
   _odsPrinter << getSrc().getType();
  _odsPrinter << ' ' << "->";
  _odsPrinter << ' ';
  {
    auto type = getResult().getType();
    if (auto validType = ::llvm::dyn_cast<::mlir::RankedTensorType>(type))
      _odsPrinter.printStrippedAttrOrType(validType);
   else
     _odsPrinter << type;
  }
}

void LocalLoadOp::getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects) {
  effects.emplace_back(::mlir::MemoryEffects::Read::get(), 0, false, ::mlir::triton::gpu::SharedMemory::get());
}

} // namespace gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::gpu::LocalLoadOp)

namespace mlir {
namespace triton {
namespace gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::gpu::MemDescSubviewOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
MemDescSubviewOpGenericAdaptorBase::MemDescSubviewOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const ::mlir::EmptyProperties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_gpu.memdesc_subview", odsAttrs.getContext());
}

MemDescSubviewOpGenericAdaptorBase::MemDescSubviewOpGenericAdaptorBase(MemDescSubviewOp op) : MemDescSubviewOpGenericAdaptorBase(op->getAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> MemDescSubviewOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  bool isVariadic[] = {false, true};
  int prevVariadicCount = 0;
  for (unsigned i = 0; i < index; ++i)
    if (isVariadic[i]) ++prevVariadicCount;

  // Calculate how many dynamic values a static variadic operand corresponds to.
  // This assumes all static variadic operands have the same dynamic value count.
  int variadicSize = (odsOperandsSize - 1) / 1;
  // `index` passed in as the parameter is the static index which counts each
  // operand (variadic or not) as size 1. So here for each previous static variadic
  // operand, we need to offset by (variadicSize - 1) to get where the dynamic
  // value pack for this static operand starts.
  int start = index + (variadicSize - 1) * prevVariadicCount;
  int size = isVariadic[index] ? variadicSize : 1;
  return {start, size};
}

::mlir::DictionaryAttr MemDescSubviewOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

} // namespace detail
MemDescSubviewOpAdaptor::MemDescSubviewOpAdaptor(MemDescSubviewOp op) : MemDescSubviewOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult MemDescSubviewOpAdaptor::verify(::mlir::Location loc) {
  return ::mlir::success();
}

std::pair<unsigned, unsigned> MemDescSubviewOp::getODSOperandIndexAndLength(unsigned index) {
  bool isVariadic[] = {false, true};
  int prevVariadicCount = 0;
  for (unsigned i = 0; i < index; ++i)
    if (isVariadic[i]) ++prevVariadicCount;

  // Calculate how many dynamic values a static variadic operand corresponds to.
  // This assumes all static variadic operands have the same dynamic value count.
  int variadicSize = (getOperation()->getNumOperands() - 1) / 1;
  // `index` passed in as the parameter is the static index which counts each
  // operand (variadic or not) as size 1. So here for each previous static variadic
  // operand, we need to offset by (variadicSize - 1) to get where the dynamic
  // value pack for this static operand starts.
  int start = index + (variadicSize - 1) * prevVariadicCount;
  int size = isVariadic[index] ? variadicSize : 1;
  return {start, size};
}

::mlir::Operation::operand_range MemDescSubviewOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::triton::MemDescType> MemDescSubviewOp::getDesc() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::triton::MemDescType>>(*getODSOperands(0).begin());
}

::mlir::Operation::operand_range MemDescSubviewOp::getOffsets() {
  return getODSOperands(1);
}

::mlir::OpOperand &MemDescSubviewOp::getDescMutable() {
  auto range = getODSOperandIndexAndLength(0);
  return getOperation()->getOpOperand(range.first);
}

::mlir::MutableOperandRange MemDescSubviewOp::getOffsetsMutable() {
  auto range = getODSOperandIndexAndLength(1);
  auto mutableRange = ::mlir::MutableOperandRange(getOperation(), range.first, range.second);
  return mutableRange;
}

std::pair<unsigned, unsigned> MemDescSubviewOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range MemDescSubviewOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::triton::MemDescType> MemDescSubviewOp::getResult() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::triton::MemDescType>>(*getODSResults(0).begin());
}

void MemDescSubviewOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value desc, ::mlir::ValueRange offsets) {
  odsState.addOperands(desc);
  odsState.addOperands(offsets);
  odsState.addTypes(result);
}

void MemDescSubviewOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value desc, ::mlir::ValueRange offsets) {
  odsState.addOperands(desc);
  odsState.addOperands(offsets);
  assert(resultTypes.size() == 1u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void MemDescSubviewOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() >= 1u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 1u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

::mlir::LogicalResult MemDescSubviewOp::verifyInvariantsImpl() {
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSOperands(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps3(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
    auto valueGroup1 = getODSOperands(1);

    for (auto v : valueGroup1) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps7(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
  }
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSResults(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps3(*this, v.getType(), "result", index++)))
        return ::mlir::failure();
    }
  }
  return ::mlir::success();
}

::mlir::LogicalResult MemDescSubviewOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult MemDescSubviewOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::mlir::OpAsmParser::UnresolvedOperand descRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> descOperands(descRawOperands);  ::llvm::SMLoc descOperandsLoc;
  (void)descOperandsLoc;
  ::llvm::SmallVector<::mlir::OpAsmParser::UnresolvedOperand, 4> offsetsOperands;
  ::llvm::SMLoc offsetsOperandsLoc;
  (void)offsetsOperandsLoc;
  ::mlir::Type descRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> descTypes(descRawTypes);
  ::mlir::Type resultRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> resultTypes(resultRawTypes);

  descOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperand(descRawOperands[0]))
    return ::mlir::failure();
  if (parser.parseLSquare())
    return ::mlir::failure();

  offsetsOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperandList(offsetsOperands))
    return ::mlir::failure();
  if (parser.parseRSquare())
    return ::mlir::failure();
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
  }
  if (parser.parseColon())
    return ::mlir::failure();

  if (parser.parseType(descRawTypes[0]))
    return ::mlir::failure();
  if (parser.parseArrow())
    return ::mlir::failure();

  if (parser.parseType(resultRawTypes[0]))
    return ::mlir::failure();
  ::mlir::Type odsBuildableType0 = parser.getBuilder().getIntegerType(32);
  result.addTypes(resultTypes);
  if (parser.resolveOperands(descOperands, descTypes, descOperandsLoc, result.operands))
    return ::mlir::failure();
  if (parser.resolveOperands(offsetsOperands, odsBuildableType0, offsetsOperandsLoc, result.operands))
    return ::mlir::failure();
  return ::mlir::success();
}

void MemDescSubviewOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  _odsPrinter << ' ';
  _odsPrinter << getDesc();
  _odsPrinter << "[";
  _odsPrinter << getOffsets();
  _odsPrinter << "]";
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
  _odsPrinter << ' ' << ":";
  _odsPrinter << ' ';
   _odsPrinter << getDesc().getType();
  _odsPrinter << ' ' << "->";
  _odsPrinter << ' ';
   _odsPrinter << getResult().getType();
}

void MemDescSubviewOp::getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects) {
}

} // namespace gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::gpu::MemDescSubviewOp)

namespace mlir {
namespace triton {
namespace gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::gpu::SparseDotOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
SparseDotOpGenericAdaptorBase::SparseDotOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const ::mlir::EmptyProperties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_gpu.sparse_dot", odsAttrs.getContext());
}

SparseDotOpGenericAdaptorBase::SparseDotOpGenericAdaptorBase(SparseDotOp op) : SparseDotOpGenericAdaptorBase(op->getAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> SparseDotOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  return {index, 1};
}

::mlir::DictionaryAttr SparseDotOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

} // namespace detail
SparseDotOpAdaptor::SparseDotOpAdaptor(SparseDotOp op) : SparseDotOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult SparseDotOpAdaptor::verify(::mlir::Location loc) {
  return ::mlir::success();
}

std::pair<unsigned, unsigned> SparseDotOp::getODSOperandIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::operand_range SparseDotOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::TensorOrMemDesc> SparseDotOp::getA() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::TensorOrMemDesc>>(*getODSOperands(0).begin());
}

::mlir::TypedValue<::mlir::TensorOrMemDesc> SparseDotOp::getB() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::TensorOrMemDesc>>(*getODSOperands(1).begin());
}

::mlir::TypedValue<::mlir::RankedTensorType> SparseDotOp::getC() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(2).begin());
}

::mlir::TypedValue<::mlir::RankedTensorType> SparseDotOp::getAMeta() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(3).begin());
}

::mlir::OpOperand &SparseDotOp::getAMutable() {
  auto range = getODSOperandIndexAndLength(0);
  return getOperation()->getOpOperand(range.first);
}

::mlir::OpOperand &SparseDotOp::getBMutable() {
  auto range = getODSOperandIndexAndLength(1);
  return getOperation()->getOpOperand(range.first);
}

::mlir::OpOperand &SparseDotOp::getCMutable() {
  auto range = getODSOperandIndexAndLength(2);
  return getOperation()->getOpOperand(range.first);
}

::mlir::OpOperand &SparseDotOp::getAMetaMutable() {
  auto range = getODSOperandIndexAndLength(3);
  return getOperation()->getOpOperand(range.first);
}

std::pair<unsigned, unsigned> SparseDotOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range SparseDotOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::RankedTensorType> SparseDotOp::getD() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
}

void SparseDotOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type d, ::mlir::Value a, ::mlir::Value b, ::mlir::Value c, ::mlir::Value aMeta) {
  odsState.addOperands(a);
  odsState.addOperands(b);
  odsState.addOperands(c);
  odsState.addOperands(aMeta);
  odsState.addTypes(d);
}

void SparseDotOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value a, ::mlir::Value b, ::mlir::Value c, ::mlir::Value aMeta) {
  odsState.addOperands(a);
  odsState.addOperands(b);
  odsState.addOperands(c);
  odsState.addOperands(aMeta);

        ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
        if (::mlir::succeeded(SparseDotOp::inferReturnTypes(odsBuilder.getContext(),
                      odsState.location, odsState.operands,
                      odsState.attributes.getDictionary(odsState.getContext()),
                      odsState.getRawProperties(),
                      odsState.regions, inferredReturnTypes)))
          odsState.addTypes(inferredReturnTypes);
        else
          ::llvm::report_fatal_error("Failed to infer result type(s).");
}

void SparseDotOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value a, ::mlir::Value b, ::mlir::Value c, ::mlir::Value aMeta) {
  odsState.addOperands(a);
  odsState.addOperands(b);
  odsState.addOperands(c);
  odsState.addOperands(aMeta);
  assert(resultTypes.size() == 1u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void SparseDotOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 4u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 1u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

void SparseDotOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 4u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);

  ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
  if (::mlir::succeeded(SparseDotOp::inferReturnTypes(odsBuilder.getContext(),
          odsState.location, operands,
          odsState.attributes.getDictionary(odsState.getContext()),
          odsState.getRawProperties(),
          odsState.regions, inferredReturnTypes))) {
    assert(inferredReturnTypes.size() == 1u && "mismatched number of return types");
    odsState.addTypes(inferredReturnTypes);
  } else {
    ::llvm::report_fatal_error("Failed to infer result type(s).");
  }
}

::mlir::LogicalResult SparseDotOp::verifyInvariantsImpl() {
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSOperands(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps8(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
    auto valueGroup1 = getODSOperands(1);

    for (auto v : valueGroup1) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps8(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
    auto valueGroup2 = getODSOperands(2);

    for (auto v : valueGroup2) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps9(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
    auto valueGroup3 = getODSOperands(3);

    for (auto v : valueGroup3) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps10(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
  }
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSResults(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonGPUOps9(*this, v.getType(), "result", index++)))
        return ::mlir::failure();
    }
  }
  if (!((std::equal_to<>()((*this->getODSResults(0).begin()).getType(), (*this->getODSOperands(2).begin()).getType()))))
    return emitOpError("failed to verify that result's type matches accumulator's type");
  return ::mlir::success();
}

::mlir::LogicalResult SparseDotOp::verifyInvariants() {
  if(::mlir::succeeded(verifyInvariantsImpl()) && ::mlir::succeeded(verify()))
    return ::mlir::success();
  return ::mlir::failure();
}

::mlir::ParseResult SparseDotOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::mlir::OpAsmParser::UnresolvedOperand aRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> aOperands(aRawOperands);  ::llvm::SMLoc aOperandsLoc;
  (void)aOperandsLoc;
  ::mlir::OpAsmParser::UnresolvedOperand bRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> bOperands(bRawOperands);  ::llvm::SMLoc bOperandsLoc;
  (void)bOperandsLoc;
  ::mlir::OpAsmParser::UnresolvedOperand cRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> cOperands(cRawOperands);  ::llvm::SMLoc cOperandsLoc;
  (void)cOperandsLoc;
  ::mlir::OpAsmParser::UnresolvedOperand aMetaRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> aMetaOperands(aMetaRawOperands);  ::llvm::SMLoc aMetaOperandsLoc;
  (void)aMetaOperandsLoc;
  ::mlir::Type aRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> aTypes(aRawTypes);
  ::mlir::Type aMetaRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> aMetaTypes(aMetaRawTypes);
  ::mlir::Type bRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> bTypes(bRawTypes);
  ::mlir::Type dRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> dTypes(dRawTypes);

  aOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperand(aRawOperands[0]))
    return ::mlir::failure();
  if (parser.parseComma())
    return ::mlir::failure();

  bOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperand(bRawOperands[0]))
    return ::mlir::failure();
  if (parser.parseComma())
    return ::mlir::failure();

  cOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperand(cRawOperands[0]))
    return ::mlir::failure();
  if (parser.parseComma())
    return ::mlir::failure();

  aMetaOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperand(aMetaRawOperands[0]))
    return ::mlir::failure();
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
  }
  if (parser.parseColon())
    return ::mlir::failure();

  {
    ::mlir::TensorOrMemDesc type;
    if (parser.parseCustomTypeWithFallback(type))
      return ::mlir::failure();
    aRawTypes[0] = type;
  }
  if (parser.parseKeyword("meta"))
    return ::mlir::failure();

  {
    ::mlir::RankedTensorType type;
    if (parser.parseCustomTypeWithFallback(type))
      return ::mlir::failure();
    aMetaRawTypes[0] = type;
  }
  if (parser.parseStar())
    return ::mlir::failure();

  {
    ::mlir::TensorOrMemDesc type;
    if (parser.parseCustomTypeWithFallback(type))
      return ::mlir::failure();
    bRawTypes[0] = type;
  }
  if (parser.parseArrow())
    return ::mlir::failure();

  {
    ::mlir::RankedTensorType type;
    if (parser.parseCustomTypeWithFallback(type))
      return ::mlir::failure();
    dRawTypes[0] = type;
  }
  for (::mlir::Type type : dTypes) {
    (void)type;
    if (!(((::llvm::isa<::mlir::RankedTensorType>(type))) && ([](::mlir::Type elementType) { return (((elementType.isFloat8E4M3FNUZ())) || ((elementType.isFloat8E4M3FN())) || ((elementType.isFloat8E4M3B11FNUZ())) || ((elementType.isFloat8E5M2())) || ((elementType.isFloat8E5M2FNUZ())) || ((elementType.isF16())) || ((elementType.isBF16())) || ((elementType.isF32())) || ((elementType.isF64()))) || (((elementType.isSignlessInteger(1))) || ((elementType.isSignlessInteger(8))) || ((elementType.isSignlessInteger(16))) || ((elementType.isSignlessInteger(32))) || ((elementType.isSignlessInteger(64)))); }(::llvm::cast<::mlir::ShapedType>(type).getElementType())))) {
      return parser.emitError(parser.getNameLoc()) << "'d' must be ranked tensor of floating-point or integer values, but got " << type;
    }
  }
  result.addTypes(dTypes);
  if (parser.resolveOperands(aOperands, aTypes, aOperandsLoc, result.operands))
    return ::mlir::failure();
  if (parser.resolveOperands(bOperands, bTypes, bOperandsLoc, result.operands))
    return ::mlir::failure();
  if (parser.resolveOperands(cOperands, dTypes[0], cOperandsLoc, result.operands))
    return ::mlir::failure();
  if (parser.resolveOperands(aMetaOperands, aMetaTypes, aMetaOperandsLoc, result.operands))
    return ::mlir::failure();
  return ::mlir::success();
}

void SparseDotOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  _odsPrinter << ' ';
  _odsPrinter << getA();
  _odsPrinter << ",";
  _odsPrinter << ' ';
  _odsPrinter << getB();
  _odsPrinter << ",";
  _odsPrinter << ' ';
  _odsPrinter << getC();
  _odsPrinter << ",";
  _odsPrinter << ' ';
  _odsPrinter << getAMeta();
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
  _odsPrinter << ' ' << ":";
  _odsPrinter << ' ';
  {
    auto type = getA().getType();
    if (auto validType = ::llvm::dyn_cast<::mlir::TensorOrMemDesc>(type))
      _odsPrinter.printStrippedAttrOrType(validType);
   else
     _odsPrinter << type;
  }
  _odsPrinter << ' ' << "meta";
  _odsPrinter << ' ';
  {
    auto type = getAMeta().getType();
    if (auto validType = ::llvm::dyn_cast<::mlir::RankedTensorType>(type))
      _odsPrinter.printStrippedAttrOrType(validType);
   else
     _odsPrinter << type;
  }
  _odsPrinter << ' ' << "*";
  _odsPrinter << ' ';
  {
    auto type = getB().getType();
    if (auto validType = ::llvm::dyn_cast<::mlir::TensorOrMemDesc>(type))
      _odsPrinter.printStrippedAttrOrType(validType);
   else
     _odsPrinter << type;
  }
  _odsPrinter << ' ' << "->";
  _odsPrinter << ' ';
  {
    auto type = getD().getType();
    if (auto validType = ::llvm::dyn_cast<::mlir::RankedTensorType>(type))
      _odsPrinter.printStrippedAttrOrType(validType);
   else
     _odsPrinter << type;
  }
}

void SparseDotOp::getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects) {
}

} // namespace gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::gpu::SparseDotOp)


#endif  // GET_OP_CLASSES

