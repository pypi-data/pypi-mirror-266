/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Op Definitions                                                             *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|* From: TritonNvidiaGPUOps.td                                                *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

#ifdef GET_OP_LIST
#undef GET_OP_LIST

::mlir::triton::nvidia_gpu::ClusterArriveOp,
::mlir::triton::nvidia_gpu::ClusterWaitOp,
::mlir::triton::nvidia_gpu::DotAsyncOp,
::mlir::triton::nvidia_gpu::DotWaitOp,
::mlir::triton::nvidia_gpu::FenceAsyncSharedOp,
::mlir::triton::nvidia_gpu::GetClusterCTAIdOp
#endif  // GET_OP_LIST

#ifdef GET_OP_CLASSES
#undef GET_OP_CLASSES


//===----------------------------------------------------------------------===//
// Local Utility Method Definitions
//===----------------------------------------------------------------------===//

namespace mlir {
namespace triton {
namespace nvidia_gpu {

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonNvidiaGPUOps0(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!((::llvm::isa<::mlir::TensorOrMemDesc>(type)))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be TensorOrMemDesc instance, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonNvidiaGPUOps1(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!(((::llvm::isa<::mlir::RankedTensorType>(type))) && ([](::mlir::Type elementType) { return (((elementType.isFloat8E4M3FNUZ())) || ((elementType.isFloat8E4M3FN())) || ((elementType.isFloat8E4M3B11FNUZ())) || ((elementType.isFloat8E5M2())) || ((elementType.isFloat8E5M2FNUZ())) || ((elementType.isF16())) || ((elementType.isBF16())) || ((elementType.isF32())) || ((elementType.isF64()))) || (((elementType.isSignlessInteger(1))) || ((elementType.isSignlessInteger(8))) || ((elementType.isSignlessInteger(16))) || ((elementType.isSignlessInteger(32))) || ((elementType.isSignlessInteger(64)))); }(::llvm::cast<::mlir::ShapedType>(type).getElementType())))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be ranked tensor of floating-point or integer values, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonNvidiaGPUOps2(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!((::llvm::isa<::mlir::TensorOrMemDesc>(type)))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be variadic of TensorOrMemDesc instance, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_type_constraint_TritonNvidiaGPUOps3(
    ::mlir::Operation *op, ::mlir::Type type, ::llvm::StringRef valueKind,
    unsigned valueIndex) {
  if (!((type.isSignlessInteger(32)))) {
    return op->emitOpError(valueKind) << " #" << valueIndex
        << " must be 32-bit signless integer, but got " << type;
  }
  return ::mlir::success();
}

static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonNvidiaGPUOps0(
    ::mlir::Attribute attr, ::llvm::StringRef attrName, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  if (attr && !(((::llvm::isa<::mlir::IntegerAttr>(attr))) && ((::llvm::cast<::mlir::IntegerAttr>(attr).getType().isSignlessInteger(1)))))
    return emitError() << "attribute '" << attrName
        << "' failed to satisfy constraint: 1-bit signless integer attribute";
  return ::mlir::success();
}
static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonNvidiaGPUOps0(
    ::mlir::Operation *op, ::mlir::Attribute attr, ::llvm::StringRef attrName) {
  return __mlir_ods_local_attr_constraint_TritonNvidiaGPUOps0(attr, attrName, [op]() {
    return op->emitOpError();
  });
}

static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonNvidiaGPUOps1(
    ::mlir::Attribute attr, ::llvm::StringRef attrName, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  if (attr && !((::llvm::isa<::mlir::BoolAttr>(attr))))
    return emitError() << "attribute '" << attrName
        << "' failed to satisfy constraint: bool attribute";
  return ::mlir::success();
}
static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonNvidiaGPUOps1(
    ::mlir::Operation *op, ::mlir::Attribute attr, ::llvm::StringRef attrName) {
  return __mlir_ods_local_attr_constraint_TritonNvidiaGPUOps1(attr, attrName, [op]() {
    return op->emitOpError();
  });
}

static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonNvidiaGPUOps2(
    ::mlir::Attribute attr, ::llvm::StringRef attrName, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  if (attr && !(((::llvm::isa<::mlir::IntegerAttr>(attr))) && ((::llvm::cast<::mlir::IntegerAttr>(attr).getType().isSignlessInteger(32)))))
    return emitError() << "attribute '" << attrName
        << "' failed to satisfy constraint: 32-bit signless integer attribute";
  return ::mlir::success();
}
static ::mlir::LogicalResult __mlir_ods_local_attr_constraint_TritonNvidiaGPUOps2(
    ::mlir::Operation *op, ::mlir::Attribute attr, ::llvm::StringRef attrName) {
  return __mlir_ods_local_attr_constraint_TritonNvidiaGPUOps2(attr, attrName, [op]() {
    return op->emitOpError();
  });
}
} // namespace nvidia_gpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace nvidia_gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::nvidia_gpu::ClusterArriveOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
ClusterArriveOpGenericAdaptorBase::ClusterArriveOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_nvidia_gpu.cluster_arrive", odsAttrs.getContext());
}

ClusterArriveOpGenericAdaptorBase::ClusterArriveOpGenericAdaptorBase(ClusterArriveOp op) : ClusterArriveOpGenericAdaptorBase(op->getDiscardableAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> ClusterArriveOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  return {index, 1};
}

::mlir::DictionaryAttr ClusterArriveOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

::mlir::IntegerAttr ClusterArriveOpGenericAdaptorBase::getRelaxedAttr() {
  auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().relaxed);
  return attr;
}

bool ClusterArriveOpGenericAdaptorBase::getRelaxed() {
  auto attr = getRelaxedAttr();
  return attr.getValue().getZExtValue();
}

} // namespace detail
ClusterArriveOpAdaptor::ClusterArriveOpAdaptor(ClusterArriveOp op) : ClusterArriveOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult ClusterArriveOpAdaptor::verify(::mlir::Location loc) {
  auto tblgen_relaxed = getProperties().relaxed; (void)tblgen_relaxed;
  if (!tblgen_relaxed) return emitError(loc, "'triton_nvidia_gpu.cluster_arrive' op ""requires attribute 'relaxed'");

  if (tblgen_relaxed && !(((::llvm::isa<::mlir::IntegerAttr>(tblgen_relaxed))) && ((::llvm::cast<::mlir::IntegerAttr>(tblgen_relaxed).getType().isSignlessInteger(1)))))
    return emitError(loc, "'triton_nvidia_gpu.cluster_arrive' op ""attribute 'relaxed' failed to satisfy constraint: 1-bit signless integer attribute");
  return ::mlir::success();
}

std::pair<unsigned, unsigned> ClusterArriveOp::getODSOperandIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::operand_range ClusterArriveOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

std::pair<unsigned, unsigned> ClusterArriveOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range ClusterArriveOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::LogicalResult ClusterArriveOp::setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  ::mlir::DictionaryAttr dict = ::llvm::dyn_cast<::mlir::DictionaryAttr>(attr);
  if (!dict) {
    emitError() << "expected DictionaryAttr to set properties";
    return ::mlir::failure();
  }

  {
    auto &propStorage = prop.relaxed;
       auto attr = dict.get("relaxed");
    if (attr || /*isRequired=*/true) {
      if (!attr) {
        emitError() << "expected key entry for relaxed in DictionaryAttr to set "
                   "Properties.";
        return ::mlir::failure();
      }
      auto convertedAttr = ::llvm::dyn_cast<std::remove_reference_t<decltype(propStorage)>>(attr);
      if (convertedAttr) {
        propStorage = convertedAttr;
      } else {
        emitError() << "Invalid attribute `relaxed` in property conversion: " << attr;
        return ::mlir::failure();
      }
    }
  }
  return ::mlir::success();
}

::mlir::Attribute ClusterArriveOp::getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop) {
    ::mlir::SmallVector<::mlir::NamedAttribute> attrs;
    ::mlir::Builder odsBuilder{ctx};

    {
      const auto &propStorage = prop.relaxed;
      if (propStorage)
        attrs.push_back(odsBuilder.getNamedAttr("relaxed",
                                       propStorage));
    }

  if (!attrs.empty())
    return odsBuilder.getDictionaryAttr(attrs);
  return {};
}

llvm::hash_code ClusterArriveOp::computePropertiesHash(const Properties &prop) {
  return llvm::hash_combine(
    llvm::hash_value(prop.relaxed.getAsOpaquePointer()));
}

std::optional<mlir::Attribute> ClusterArriveOp::getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name) {
    if (name == "relaxed")
      return prop.relaxed;
  return std::nullopt;
}

void ClusterArriveOp::setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value) {
    if (name == "relaxed") {
       prop.relaxed = ::llvm::dyn_cast_or_null<std::remove_reference_t<decltype(prop.relaxed)>>(value);
       return;
    }
}

void ClusterArriveOp::populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs) {
    if (prop.relaxed) attrs.append("relaxed", prop.relaxed);
}

::mlir::LogicalResult ClusterArriveOp::verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
    {
      ::mlir::Attribute attr = attrs.get(getRelaxedAttrName(opName));
      if (attr && ::mlir::failed(__mlir_ods_local_attr_constraint_TritonNvidiaGPUOps0(attr, "relaxed", emitError)))
        return ::mlir::failure();
    }
    return ::mlir::success();
}

::mlir::LogicalResult ClusterArriveOp::readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state) {
  auto &prop = state.getOrAddProperties<Properties>(); (void)prop;
  if (::mlir::failed(reader.readAttribute(prop.relaxed)))
    return ::mlir::failure();
  return ::mlir::success();
}

void ClusterArriveOp::writeProperties(::mlir::DialectBytecodeWriter &writer) {
  auto &prop = getProperties(); (void)prop;
  writer.writeAttribute(prop.relaxed);
}

::mlir::IntegerAttr ClusterArriveOp::getRelaxedAttr() {
  return ::llvm::cast<::mlir::IntegerAttr>(getProperties().relaxed);
}

bool ClusterArriveOp::getRelaxed() {
  auto attr = getRelaxedAttr();
  return attr.getValue().getZExtValue();
}

void ClusterArriveOp::setRelaxedAttr(::mlir::IntegerAttr attr) {
  getProperties().relaxed = attr;
}

void ClusterArriveOp::setRelaxed(bool attrValue) {
  getProperties().relaxed = ::mlir::Builder((*this)->getContext()).getIntegerAttr(::mlir::Builder((*this)->getContext()).getIntegerType(1), attrValue);
}

void ClusterArriveOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::IntegerAttr relaxed) {
  odsState.getOrAddProperties<Properties>().relaxed = relaxed;
}

void ClusterArriveOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::IntegerAttr relaxed) {
  odsState.getOrAddProperties<Properties>().relaxed = relaxed;
  assert(resultTypes.size() == 0u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void ClusterArriveOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, bool relaxed) {
  odsState.getOrAddProperties<Properties>().relaxed = odsBuilder.getIntegerAttr(odsBuilder.getIntegerType(1), relaxed);
}

void ClusterArriveOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, bool relaxed) {
  odsState.getOrAddProperties<Properties>().relaxed = odsBuilder.getIntegerAttr(odsBuilder.getIntegerType(1), relaxed);
  assert(resultTypes.size() == 0u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void ClusterArriveOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 0u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 0u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

::mlir::LogicalResult ClusterArriveOp::verifyInvariantsImpl() {
  auto tblgen_relaxed = getProperties().relaxed; (void)tblgen_relaxed;
  if (!tblgen_relaxed) return emitOpError("requires attribute 'relaxed'");

  if (::mlir::failed(__mlir_ods_local_attr_constraint_TritonNvidiaGPUOps0(*this, tblgen_relaxed, "relaxed")))
    return ::mlir::failure();
  return ::mlir::success();
}

::mlir::LogicalResult ClusterArriveOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult ClusterArriveOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
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

void ClusterArriveOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
}

} // namespace nvidia_gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::nvidia_gpu::ClusterArriveOp)

namespace mlir {
namespace triton {
namespace nvidia_gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::nvidia_gpu::ClusterWaitOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
ClusterWaitOpGenericAdaptorBase::ClusterWaitOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const ::mlir::EmptyProperties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_nvidia_gpu.cluster_wait", odsAttrs.getContext());
}

ClusterWaitOpGenericAdaptorBase::ClusterWaitOpGenericAdaptorBase(ClusterWaitOp op) : ClusterWaitOpGenericAdaptorBase(op->getAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> ClusterWaitOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  return {index, 1};
}

::mlir::DictionaryAttr ClusterWaitOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

} // namespace detail
ClusterWaitOpAdaptor::ClusterWaitOpAdaptor(ClusterWaitOp op) : ClusterWaitOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult ClusterWaitOpAdaptor::verify(::mlir::Location loc) {
  return ::mlir::success();
}

std::pair<unsigned, unsigned> ClusterWaitOp::getODSOperandIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::operand_range ClusterWaitOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

std::pair<unsigned, unsigned> ClusterWaitOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range ClusterWaitOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

void ClusterWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState) {
}

void ClusterWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes) {
  assert(resultTypes.size() == 0u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void ClusterWaitOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 0u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 0u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

::mlir::LogicalResult ClusterWaitOp::verifyInvariantsImpl() {
  return ::mlir::success();
}

::mlir::LogicalResult ClusterWaitOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult ClusterWaitOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
  }
  return ::mlir::success();
}

void ClusterWaitOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
}

} // namespace nvidia_gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::nvidia_gpu::ClusterWaitOp)

namespace mlir {
namespace triton {
namespace nvidia_gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::nvidia_gpu::DotAsyncOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
DotAsyncOpGenericAdaptorBase::DotAsyncOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_nvidia_gpu.dot_async", odsAttrs.getContext());
}

DotAsyncOpGenericAdaptorBase::DotAsyncOpGenericAdaptorBase(DotAsyncOp op) : DotAsyncOpGenericAdaptorBase(op->getDiscardableAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> DotAsyncOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  return {index, 1};
}

::mlir::DictionaryAttr DotAsyncOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

::mlir::BoolAttr DotAsyncOpGenericAdaptorBase::getAllowTF32Attr() {
  auto attr = ::llvm::cast<::mlir::BoolAttr>(getProperties().allowTF32);
  return attr;
}

bool DotAsyncOpGenericAdaptorBase::getAllowTF32() {
  auto attr = getAllowTF32Attr();
  return attr.getValue();
}

::mlir::IntegerAttr DotAsyncOpGenericAdaptorBase::getMaxNumImpreciseAccAttr() {
  auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().maxNumImpreciseAcc);
  return attr;
}

uint32_t DotAsyncOpGenericAdaptorBase::getMaxNumImpreciseAcc() {
  auto attr = getMaxNumImpreciseAccAttr();
  return attr.getValue().getZExtValue();
}

} // namespace detail
DotAsyncOpAdaptor::DotAsyncOpAdaptor(DotAsyncOp op) : DotAsyncOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult DotAsyncOpAdaptor::verify(::mlir::Location loc) {
  auto tblgen_allowTF32 = getProperties().allowTF32; (void)tblgen_allowTF32;
  if (!tblgen_allowTF32) return emitError(loc, "'triton_nvidia_gpu.dot_async' op ""requires attribute 'allowTF32'");
  auto tblgen_maxNumImpreciseAcc = getProperties().maxNumImpreciseAcc; (void)tblgen_maxNumImpreciseAcc;
  if (!tblgen_maxNumImpreciseAcc) return emitError(loc, "'triton_nvidia_gpu.dot_async' op ""requires attribute 'maxNumImpreciseAcc'");

  if (tblgen_allowTF32 && !((::llvm::isa<::mlir::BoolAttr>(tblgen_allowTF32))))
    return emitError(loc, "'triton_nvidia_gpu.dot_async' op ""attribute 'allowTF32' failed to satisfy constraint: bool attribute");

  if (tblgen_maxNumImpreciseAcc && !(((::llvm::isa<::mlir::IntegerAttr>(tblgen_maxNumImpreciseAcc))) && ((::llvm::cast<::mlir::IntegerAttr>(tblgen_maxNumImpreciseAcc).getType().isSignlessInteger(32)))))
    return emitError(loc, "'triton_nvidia_gpu.dot_async' op ""attribute 'maxNumImpreciseAcc' failed to satisfy constraint: 32-bit signless integer attribute");
  return ::mlir::success();
}

std::pair<unsigned, unsigned> DotAsyncOp::getODSOperandIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::operand_range DotAsyncOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::TensorOrMemDesc> DotAsyncOp::getA() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::TensorOrMemDesc>>(*getODSOperands(0).begin());
}

::mlir::TypedValue<::mlir::TensorOrMemDesc> DotAsyncOp::getB() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::TensorOrMemDesc>>(*getODSOperands(1).begin());
}

::mlir::TypedValue<::mlir::RankedTensorType> DotAsyncOp::getC() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(2).begin());
}

::mlir::OpOperand &DotAsyncOp::getAMutable() {
  auto range = getODSOperandIndexAndLength(0);
  return getOperation()->getOpOperand(range.first);
}

::mlir::OpOperand &DotAsyncOp::getBMutable() {
  auto range = getODSOperandIndexAndLength(1);
  return getOperation()->getOpOperand(range.first);
}

::mlir::OpOperand &DotAsyncOp::getCMutable() {
  auto range = getODSOperandIndexAndLength(2);
  return getOperation()->getOpOperand(range.first);
}

std::pair<unsigned, unsigned> DotAsyncOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range DotAsyncOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::RankedTensorType> DotAsyncOp::getD() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
}

::mlir::LogicalResult DotAsyncOp::setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  ::mlir::DictionaryAttr dict = ::llvm::dyn_cast<::mlir::DictionaryAttr>(attr);
  if (!dict) {
    emitError() << "expected DictionaryAttr to set properties";
    return ::mlir::failure();
  }

  {
    auto &propStorage = prop.allowTF32;
       auto attr = dict.get("allowTF32");
    if (attr || /*isRequired=*/true) {
      if (!attr) {
        emitError() << "expected key entry for allowTF32 in DictionaryAttr to set "
                   "Properties.";
        return ::mlir::failure();
      }
      auto convertedAttr = ::llvm::dyn_cast<std::remove_reference_t<decltype(propStorage)>>(attr);
      if (convertedAttr) {
        propStorage = convertedAttr;
      } else {
        emitError() << "Invalid attribute `allowTF32` in property conversion: " << attr;
        return ::mlir::failure();
      }
    }
  }

  {
    auto &propStorage = prop.maxNumImpreciseAcc;
       auto attr = dict.get("maxNumImpreciseAcc");
    if (attr || /*isRequired=*/true) {
      if (!attr) {
        emitError() << "expected key entry for maxNumImpreciseAcc in DictionaryAttr to set "
                   "Properties.";
        return ::mlir::failure();
      }
      auto convertedAttr = ::llvm::dyn_cast<std::remove_reference_t<decltype(propStorage)>>(attr);
      if (convertedAttr) {
        propStorage = convertedAttr;
      } else {
        emitError() << "Invalid attribute `maxNumImpreciseAcc` in property conversion: " << attr;
        return ::mlir::failure();
      }
    }
  }
  return ::mlir::success();
}

::mlir::Attribute DotAsyncOp::getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop) {
    ::mlir::SmallVector<::mlir::NamedAttribute> attrs;
    ::mlir::Builder odsBuilder{ctx};

    {
      const auto &propStorage = prop.allowTF32;
      if (propStorage)
        attrs.push_back(odsBuilder.getNamedAttr("allowTF32",
                                       propStorage));
    }

    {
      const auto &propStorage = prop.maxNumImpreciseAcc;
      if (propStorage)
        attrs.push_back(odsBuilder.getNamedAttr("maxNumImpreciseAcc",
                                       propStorage));
    }

  if (!attrs.empty())
    return odsBuilder.getDictionaryAttr(attrs);
  return {};
}

llvm::hash_code DotAsyncOp::computePropertiesHash(const Properties &prop) {
  return llvm::hash_combine(
    llvm::hash_value(prop.allowTF32.getAsOpaquePointer()), 
    llvm::hash_value(prop.maxNumImpreciseAcc.getAsOpaquePointer()));
}

std::optional<mlir::Attribute> DotAsyncOp::getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name) {
    if (name == "allowTF32")
      return prop.allowTF32;

    if (name == "maxNumImpreciseAcc")
      return prop.maxNumImpreciseAcc;
  return std::nullopt;
}

void DotAsyncOp::setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value) {
    if (name == "allowTF32") {
       prop.allowTF32 = ::llvm::dyn_cast_or_null<std::remove_reference_t<decltype(prop.allowTF32)>>(value);
       return;
    }

    if (name == "maxNumImpreciseAcc") {
       prop.maxNumImpreciseAcc = ::llvm::dyn_cast_or_null<std::remove_reference_t<decltype(prop.maxNumImpreciseAcc)>>(value);
       return;
    }
}

void DotAsyncOp::populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs) {
    if (prop.allowTF32) attrs.append("allowTF32", prop.allowTF32);

    if (prop.maxNumImpreciseAcc) attrs.append("maxNumImpreciseAcc", prop.maxNumImpreciseAcc);
}

::mlir::LogicalResult DotAsyncOp::verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
    {
      ::mlir::Attribute attr = attrs.get(getAllowTF32AttrName(opName));
      if (attr && ::mlir::failed(__mlir_ods_local_attr_constraint_TritonNvidiaGPUOps1(attr, "allowTF32", emitError)))
        return ::mlir::failure();
    }

    {
      ::mlir::Attribute attr = attrs.get(getMaxNumImpreciseAccAttrName(opName));
      if (attr && ::mlir::failed(__mlir_ods_local_attr_constraint_TritonNvidiaGPUOps2(attr, "maxNumImpreciseAcc", emitError)))
        return ::mlir::failure();
    }
    return ::mlir::success();
}

::mlir::LogicalResult DotAsyncOp::readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state) {
  auto &prop = state.getOrAddProperties<Properties>(); (void)prop;
  if (::mlir::failed(reader.readAttribute(prop.allowTF32)))
    return ::mlir::failure();

  if (::mlir::failed(reader.readAttribute(prop.maxNumImpreciseAcc)))
    return ::mlir::failure();
  return ::mlir::success();
}

void DotAsyncOp::writeProperties(::mlir::DialectBytecodeWriter &writer) {
  auto &prop = getProperties(); (void)prop;
  writer.writeAttribute(prop.allowTF32);
  writer.writeAttribute(prop.maxNumImpreciseAcc);
}

::mlir::BoolAttr DotAsyncOp::getAllowTF32Attr() {
  return ::llvm::cast<::mlir::BoolAttr>(getProperties().allowTF32);
}

bool DotAsyncOp::getAllowTF32() {
  auto attr = getAllowTF32Attr();
  return attr.getValue();
}

::mlir::IntegerAttr DotAsyncOp::getMaxNumImpreciseAccAttr() {
  return ::llvm::cast<::mlir::IntegerAttr>(getProperties().maxNumImpreciseAcc);
}

uint32_t DotAsyncOp::getMaxNumImpreciseAcc() {
  auto attr = getMaxNumImpreciseAccAttr();
  return attr.getValue().getZExtValue();
}

void DotAsyncOp::setAllowTF32Attr(::mlir::BoolAttr attr) {
  getProperties().allowTF32 = attr;
}

void DotAsyncOp::setAllowTF32(bool attrValue) {
  getProperties().allowTF32 = ::mlir::Builder((*this)->getContext()).getBoolAttr(attrValue);
}

void DotAsyncOp::setMaxNumImpreciseAccAttr(::mlir::IntegerAttr attr) {
  getProperties().maxNumImpreciseAcc = attr;
}

void DotAsyncOp::setMaxNumImpreciseAcc(uint32_t attrValue) {
  getProperties().maxNumImpreciseAcc = ::mlir::Builder((*this)->getContext()).getIntegerAttr(::mlir::Builder((*this)->getContext()).getIntegerType(32), attrValue);
}

void DotAsyncOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type d, ::mlir::Value a, ::mlir::Value b, ::mlir::Value c, ::mlir::BoolAttr allowTF32, ::mlir::IntegerAttr maxNumImpreciseAcc) {
  odsState.addOperands(a);
  odsState.addOperands(b);
  odsState.addOperands(c);
  odsState.getOrAddProperties<Properties>().allowTF32 = allowTF32;
  odsState.getOrAddProperties<Properties>().maxNumImpreciseAcc = maxNumImpreciseAcc;
  odsState.addTypes(d);
}

void DotAsyncOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value a, ::mlir::Value b, ::mlir::Value c, ::mlir::BoolAttr allowTF32, ::mlir::IntegerAttr maxNumImpreciseAcc) {
  odsState.addOperands(a);
  odsState.addOperands(b);
  odsState.addOperands(c);
  odsState.getOrAddProperties<Properties>().allowTF32 = allowTF32;
  odsState.getOrAddProperties<Properties>().maxNumImpreciseAcc = maxNumImpreciseAcc;

        ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
        if (::mlir::succeeded(DotAsyncOp::inferReturnTypes(odsBuilder.getContext(),
                      odsState.location, odsState.operands,
                      odsState.attributes.getDictionary(odsState.getContext()),
                      odsState.getRawProperties(),
                      odsState.regions, inferredReturnTypes)))
          odsState.addTypes(inferredReturnTypes);
        else
          ::llvm::report_fatal_error("Failed to infer result type(s).");
}

void DotAsyncOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value a, ::mlir::Value b, ::mlir::Value c, ::mlir::BoolAttr allowTF32, ::mlir::IntegerAttr maxNumImpreciseAcc) {
  odsState.addOperands(a);
  odsState.addOperands(b);
  odsState.addOperands(c);
  odsState.getOrAddProperties<Properties>().allowTF32 = allowTF32;
  odsState.getOrAddProperties<Properties>().maxNumImpreciseAcc = maxNumImpreciseAcc;
  assert(resultTypes.size() == 1u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void DotAsyncOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type d, ::mlir::Value a, ::mlir::Value b, ::mlir::Value c, bool allowTF32, uint32_t maxNumImpreciseAcc) {
  odsState.addOperands(a);
  odsState.addOperands(b);
  odsState.addOperands(c);
  odsState.getOrAddProperties<Properties>().allowTF32 = odsBuilder.getBoolAttr(allowTF32);
  odsState.getOrAddProperties<Properties>().maxNumImpreciseAcc = odsBuilder.getIntegerAttr(odsBuilder.getIntegerType(32), maxNumImpreciseAcc);
  odsState.addTypes(d);
}

void DotAsyncOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value a, ::mlir::Value b, ::mlir::Value c, bool allowTF32, uint32_t maxNumImpreciseAcc) {
  odsState.addOperands(a);
  odsState.addOperands(b);
  odsState.addOperands(c);
  odsState.getOrAddProperties<Properties>().allowTF32 = odsBuilder.getBoolAttr(allowTF32);
  odsState.getOrAddProperties<Properties>().maxNumImpreciseAcc = odsBuilder.getIntegerAttr(odsBuilder.getIntegerType(32), maxNumImpreciseAcc);

        ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
        if (::mlir::succeeded(DotAsyncOp::inferReturnTypes(odsBuilder.getContext(),
                      odsState.location, odsState.operands,
                      odsState.attributes.getDictionary(odsState.getContext()),
                      odsState.getRawProperties(),
                      odsState.regions, inferredReturnTypes)))
          odsState.addTypes(inferredReturnTypes);
        else
          ::llvm::report_fatal_error("Failed to infer result type(s).");
}

void DotAsyncOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value a, ::mlir::Value b, ::mlir::Value c, bool allowTF32, uint32_t maxNumImpreciseAcc) {
  odsState.addOperands(a);
  odsState.addOperands(b);
  odsState.addOperands(c);
  odsState.getOrAddProperties<Properties>().allowTF32 = odsBuilder.getBoolAttr(allowTF32);
  odsState.getOrAddProperties<Properties>().maxNumImpreciseAcc = odsBuilder.getIntegerAttr(odsBuilder.getIntegerType(32), maxNumImpreciseAcc);
  assert(resultTypes.size() == 1u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void DotAsyncOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 3u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 1u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

void DotAsyncOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 3u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);

  ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
  if (::mlir::succeeded(DotAsyncOp::inferReturnTypes(odsBuilder.getContext(),
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

::mlir::LogicalResult DotAsyncOp::verifyInvariantsImpl() {
  auto tblgen_allowTF32 = getProperties().allowTF32; (void)tblgen_allowTF32;
  if (!tblgen_allowTF32) return emitOpError("requires attribute 'allowTF32'");
  auto tblgen_maxNumImpreciseAcc = getProperties().maxNumImpreciseAcc; (void)tblgen_maxNumImpreciseAcc;
  if (!tblgen_maxNumImpreciseAcc) return emitOpError("requires attribute 'maxNumImpreciseAcc'");

  if (::mlir::failed(__mlir_ods_local_attr_constraint_TritonNvidiaGPUOps1(*this, tblgen_allowTF32, "allowTF32")))
    return ::mlir::failure();

  if (::mlir::failed(__mlir_ods_local_attr_constraint_TritonNvidiaGPUOps2(*this, tblgen_maxNumImpreciseAcc, "maxNumImpreciseAcc")))
    return ::mlir::failure();
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSOperands(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonNvidiaGPUOps0(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
    auto valueGroup1 = getODSOperands(1);

    for (auto v : valueGroup1) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonNvidiaGPUOps0(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
    auto valueGroup2 = getODSOperands(2);

    for (auto v : valueGroup2) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonNvidiaGPUOps1(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
  }
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSResults(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonNvidiaGPUOps1(*this, v.getType(), "result", index++)))
        return ::mlir::failure();
    }
  }
  if (!((std::equal_to<>()((*this->getODSResults(0).begin()).getType(), (*this->getODSOperands(2).begin()).getType()))))
    return emitOpError("failed to verify that result's type matches accumulator's type");
  return ::mlir::success();
}

::mlir::LogicalResult DotAsyncOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult DotAsyncOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::mlir::OpAsmParser::UnresolvedOperand aRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> aOperands(aRawOperands);  ::llvm::SMLoc aOperandsLoc;
  (void)aOperandsLoc;
  ::mlir::OpAsmParser::UnresolvedOperand bRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> bOperands(bRawOperands);  ::llvm::SMLoc bOperandsLoc;
  (void)bOperandsLoc;
  ::mlir::OpAsmParser::UnresolvedOperand cRawOperands[1];
  ::llvm::ArrayRef<::mlir::OpAsmParser::UnresolvedOperand> cOperands(cRawOperands);  ::llvm::SMLoc cOperandsLoc;
  (void)cOperandsLoc;
  ::mlir::Type aRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> aTypes(aRawTypes);
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
    ::mlir::TensorOrMemDesc type;
    if (parser.parseCustomTypeWithFallback(type))
      return ::mlir::failure();
    aRawTypes[0] = type;
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
  return ::mlir::success();
}

void DotAsyncOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  _odsPrinter << ' ';
  _odsPrinter << getA();
  _odsPrinter << ",";
  _odsPrinter << ' ';
  _odsPrinter << getB();
  _odsPrinter << ",";
  _odsPrinter << ' ';
  _odsPrinter << getC();
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

void DotAsyncOp::getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects) {
}

} // namespace nvidia_gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::nvidia_gpu::DotAsyncOp)

namespace mlir {
namespace triton {
namespace nvidia_gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::nvidia_gpu::DotWaitOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
DotWaitOpGenericAdaptorBase::DotWaitOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_nvidia_gpu.dot_wait", odsAttrs.getContext());
}

DotWaitOpGenericAdaptorBase::DotWaitOpGenericAdaptorBase(DotWaitOp op) : DotWaitOpGenericAdaptorBase(op->getDiscardableAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> DotWaitOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
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

::mlir::DictionaryAttr DotWaitOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

::mlir::IntegerAttr DotWaitOpGenericAdaptorBase::getPendingsAttr() {
  auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().pendings);
  return attr;
}

uint32_t DotWaitOpGenericAdaptorBase::getPendings() {
  auto attr = getPendingsAttr();
  return attr.getValue().getZExtValue();
}

} // namespace detail
DotWaitOpAdaptor::DotWaitOpAdaptor(DotWaitOp op) : DotWaitOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult DotWaitOpAdaptor::verify(::mlir::Location loc) {
  auto tblgen_pendings = getProperties().pendings; (void)tblgen_pendings;
  if (!tblgen_pendings) return emitError(loc, "'triton_nvidia_gpu.dot_wait' op ""requires attribute 'pendings'");

  if (tblgen_pendings && !(((::llvm::isa<::mlir::IntegerAttr>(tblgen_pendings))) && ((::llvm::cast<::mlir::IntegerAttr>(tblgen_pendings).getType().isSignlessInteger(32)))))
    return emitError(loc, "'triton_nvidia_gpu.dot_wait' op ""attribute 'pendings' failed to satisfy constraint: 32-bit signless integer attribute");
  return ::mlir::success();
}

std::pair<unsigned, unsigned> DotWaitOp::getODSOperandIndexAndLength(unsigned index) {
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

::mlir::Operation::operand_range DotWaitOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

::mlir::Operation::operand_range DotWaitOp::getInputs() {
  return getODSOperands(0);
}

::mlir::MutableOperandRange DotWaitOp::getInputsMutable() {
  auto range = getODSOperandIndexAndLength(0);
  auto mutableRange = ::mlir::MutableOperandRange(getOperation(), range.first, range.second);
  return mutableRange;
}

std::pair<unsigned, unsigned> DotWaitOp::getODSResultIndexAndLength(unsigned index) {
  bool isVariadic[] = {true};
  int prevVariadicCount = 0;
  for (unsigned i = 0; i < index; ++i)
    if (isVariadic[i]) ++prevVariadicCount;

  // Calculate how many dynamic values a static variadic operand corresponds to.
  // This assumes all static variadic operands have the same dynamic value count.
  int variadicSize = (getOperation()->getNumResults() - 0) / 1;
  // `index` passed in as the parameter is the static index which counts each
  // operand (variadic or not) as size 1. So here for each previous static variadic
  // operand, we need to offset by (variadicSize - 1) to get where the dynamic
  // value pack for this static operand starts.
  int start = index + (variadicSize - 1) * prevVariadicCount;
  int size = isVariadic[index] ? variadicSize : 1;
  return {start, size};
}

::mlir::Operation::result_range DotWaitOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::Operation::result_range DotWaitOp::getOutputs() {
  return getODSResults(0);
}

::mlir::LogicalResult DotWaitOp::setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  ::mlir::DictionaryAttr dict = ::llvm::dyn_cast<::mlir::DictionaryAttr>(attr);
  if (!dict) {
    emitError() << "expected DictionaryAttr to set properties";
    return ::mlir::failure();
  }

  {
    auto &propStorage = prop.pendings;
       auto attr = dict.get("pendings");
    if (attr || /*isRequired=*/true) {
      if (!attr) {
        emitError() << "expected key entry for pendings in DictionaryAttr to set "
                   "Properties.";
        return ::mlir::failure();
      }
      auto convertedAttr = ::llvm::dyn_cast<std::remove_reference_t<decltype(propStorage)>>(attr);
      if (convertedAttr) {
        propStorage = convertedAttr;
      } else {
        emitError() << "Invalid attribute `pendings` in property conversion: " << attr;
        return ::mlir::failure();
      }
    }
  }
  return ::mlir::success();
}

::mlir::Attribute DotWaitOp::getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop) {
    ::mlir::SmallVector<::mlir::NamedAttribute> attrs;
    ::mlir::Builder odsBuilder{ctx};

    {
      const auto &propStorage = prop.pendings;
      if (propStorage)
        attrs.push_back(odsBuilder.getNamedAttr("pendings",
                                       propStorage));
    }

  if (!attrs.empty())
    return odsBuilder.getDictionaryAttr(attrs);
  return {};
}

llvm::hash_code DotWaitOp::computePropertiesHash(const Properties &prop) {
  return llvm::hash_combine(
    llvm::hash_value(prop.pendings.getAsOpaquePointer()));
}

std::optional<mlir::Attribute> DotWaitOp::getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name) {
    if (name == "pendings")
      return prop.pendings;
  return std::nullopt;
}

void DotWaitOp::setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value) {
    if (name == "pendings") {
       prop.pendings = ::llvm::dyn_cast_or_null<std::remove_reference_t<decltype(prop.pendings)>>(value);
       return;
    }
}

void DotWaitOp::populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs) {
    if (prop.pendings) attrs.append("pendings", prop.pendings);
}

::mlir::LogicalResult DotWaitOp::verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
    {
      ::mlir::Attribute attr = attrs.get(getPendingsAttrName(opName));
      if (attr && ::mlir::failed(__mlir_ods_local_attr_constraint_TritonNvidiaGPUOps2(attr, "pendings", emitError)))
        return ::mlir::failure();
    }
    return ::mlir::success();
}

::mlir::LogicalResult DotWaitOp::readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state) {
  auto &prop = state.getOrAddProperties<Properties>(); (void)prop;
  if (::mlir::failed(reader.readAttribute(prop.pendings)))
    return ::mlir::failure();
  return ::mlir::success();
}

void DotWaitOp::writeProperties(::mlir::DialectBytecodeWriter &writer) {
  auto &prop = getProperties(); (void)prop;
  writer.writeAttribute(prop.pendings);
}

::mlir::IntegerAttr DotWaitOp::getPendingsAttr() {
  return ::llvm::cast<::mlir::IntegerAttr>(getProperties().pendings);
}

uint32_t DotWaitOp::getPendings() {
  auto attr = getPendingsAttr();
  return attr.getValue().getZExtValue();
}

void DotWaitOp::setPendingsAttr(::mlir::IntegerAttr attr) {
  getProperties().pendings = attr;
}

void DotWaitOp::setPendings(uint32_t attrValue) {
  getProperties().pendings = ::mlir::Builder((*this)->getContext()).getIntegerAttr(::mlir::Builder((*this)->getContext()).getIntegerType(32), attrValue);
}

void DotWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange outputs, ::mlir::ValueRange inputs, ::mlir::IntegerAttr pendings) {
  odsState.addOperands(inputs);
  odsState.getOrAddProperties<Properties>().pendings = pendings;
  odsState.addTypes(outputs);
}

void DotWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange inputs, ::mlir::IntegerAttr pendings) {
  odsState.addOperands(inputs);
  odsState.getOrAddProperties<Properties>().pendings = pendings;

        ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
        if (::mlir::succeeded(DotWaitOp::inferReturnTypes(odsBuilder.getContext(),
                      odsState.location, odsState.operands,
                      odsState.attributes.getDictionary(odsState.getContext()),
                      odsState.getRawProperties(),
                      odsState.regions, inferredReturnTypes)))
          odsState.addTypes(inferredReturnTypes);
        else
          ::llvm::report_fatal_error("Failed to infer result type(s).");
}

void DotWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange outputs, ::mlir::ValueRange inputs, uint32_t pendings) {
  odsState.addOperands(inputs);
  odsState.getOrAddProperties<Properties>().pendings = odsBuilder.getIntegerAttr(odsBuilder.getIntegerType(32), pendings);
  odsState.addTypes(outputs);
}

void DotWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange inputs, uint32_t pendings) {
  odsState.addOperands(inputs);
  odsState.getOrAddProperties<Properties>().pendings = odsBuilder.getIntegerAttr(odsBuilder.getIntegerType(32), pendings);

        ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
        if (::mlir::succeeded(DotWaitOp::inferReturnTypes(odsBuilder.getContext(),
                      odsState.location, odsState.operands,
                      odsState.attributes.getDictionary(odsState.getContext()),
                      odsState.getRawProperties(),
                      odsState.regions, inferredReturnTypes)))
          odsState.addTypes(inferredReturnTypes);
        else
          ::llvm::report_fatal_error("Failed to infer result type(s).");
}

void DotWaitOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  odsState.addTypes(resultTypes);
}

void DotWaitOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);

  ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
  if (::mlir::succeeded(DotWaitOp::inferReturnTypes(odsBuilder.getContext(),
          odsState.location, operands,
          odsState.attributes.getDictionary(odsState.getContext()),
          odsState.getRawProperties(),
          odsState.regions, inferredReturnTypes))) {
    odsState.addTypes(inferredReturnTypes);
  } else {
    ::llvm::report_fatal_error("Failed to infer result type(s).");
  }
}

::mlir::LogicalResult DotWaitOp::verifyInvariantsImpl() {
  auto tblgen_pendings = getProperties().pendings; (void)tblgen_pendings;
  if (!tblgen_pendings) return emitOpError("requires attribute 'pendings'");

  if (::mlir::failed(__mlir_ods_local_attr_constraint_TritonNvidiaGPUOps2(*this, tblgen_pendings, "pendings")))
    return ::mlir::failure();
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSOperands(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonNvidiaGPUOps2(*this, v.getType(), "operand", index++)))
        return ::mlir::failure();
    }
  }
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSResults(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonNvidiaGPUOps2(*this, v.getType(), "result", index++)))
        return ::mlir::failure();
    }
  }
  if (!(((this->getODSOperands(0).getType()) == (this->getODSResults(0).getType()) && (this->getODSResults(0).getType()) == (this->getODSOperands(0).getType()))))
    return emitOpError("failed to verify that all of {inputs, outputs} have same type");
  return ::mlir::success();
}

::mlir::LogicalResult DotWaitOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult DotWaitOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::llvm::SmallVector<::mlir::OpAsmParser::UnresolvedOperand, 4> inputsOperands;
  ::llvm::SMLoc inputsOperandsLoc;
  (void)inputsOperandsLoc;
  ::llvm::SmallVector<::mlir::Type, 1> inputsTypes;

  inputsOperandsLoc = parser.getCurrentLocation();
  if (parser.parseOperandList(inputsOperands))
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
  if (parser.parseColon())
    return ::mlir::failure();

  if (parser.parseTypeList(inputsTypes))
    return ::mlir::failure();
  if (parser.resolveOperands(inputsOperands, inputsTypes, inputsOperandsLoc, result.operands))
    return ::mlir::failure();

  ::llvm::SmallVector<::mlir::Type> inferredReturnTypes;
  if (::mlir::failed(DotWaitOp::inferReturnTypes(parser.getContext(),
      result.location, result.operands,
      result.attributes.getDictionary(parser.getContext()),
      result.getRawProperties(),
      result.regions, inferredReturnTypes)))
    return ::mlir::failure();
  result.addTypes(inferredReturnTypes);
  return ::mlir::success();
}

void DotWaitOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  _odsPrinter << ' ';
  _odsPrinter << getInputs();
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
  _odsPrinter << ' ' << ":";
  _odsPrinter << ' ';
  _odsPrinter << getInputs().getTypes();
}

} // namespace nvidia_gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::nvidia_gpu::DotWaitOp)

namespace mlir {
namespace triton {
namespace nvidia_gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::nvidia_gpu::FenceAsyncSharedOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
FenceAsyncSharedOpGenericAdaptorBase::FenceAsyncSharedOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_nvidia_gpu.fence_async_shared", odsAttrs.getContext());
}

FenceAsyncSharedOpGenericAdaptorBase::FenceAsyncSharedOpGenericAdaptorBase(FenceAsyncSharedOp op) : FenceAsyncSharedOpGenericAdaptorBase(op->getDiscardableAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> FenceAsyncSharedOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  return {index, 1};
}

::mlir::DictionaryAttr FenceAsyncSharedOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

::mlir::BoolAttr FenceAsyncSharedOpGenericAdaptorBase::getBClusterAttr() {
  auto attr = ::llvm::cast<::mlir::BoolAttr>(getProperties().bCluster);
  return attr;
}

bool FenceAsyncSharedOpGenericAdaptorBase::getBCluster() {
  auto attr = getBClusterAttr();
  return attr.getValue();
}

} // namespace detail
FenceAsyncSharedOpAdaptor::FenceAsyncSharedOpAdaptor(FenceAsyncSharedOp op) : FenceAsyncSharedOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult FenceAsyncSharedOpAdaptor::verify(::mlir::Location loc) {
  auto tblgen_bCluster = getProperties().bCluster; (void)tblgen_bCluster;
  if (!tblgen_bCluster) return emitError(loc, "'triton_nvidia_gpu.fence_async_shared' op ""requires attribute 'bCluster'");

  if (tblgen_bCluster && !((::llvm::isa<::mlir::BoolAttr>(tblgen_bCluster))))
    return emitError(loc, "'triton_nvidia_gpu.fence_async_shared' op ""attribute 'bCluster' failed to satisfy constraint: bool attribute");
  return ::mlir::success();
}

std::pair<unsigned, unsigned> FenceAsyncSharedOp::getODSOperandIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::operand_range FenceAsyncSharedOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

std::pair<unsigned, unsigned> FenceAsyncSharedOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range FenceAsyncSharedOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::LogicalResult FenceAsyncSharedOp::setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
  ::mlir::DictionaryAttr dict = ::llvm::dyn_cast<::mlir::DictionaryAttr>(attr);
  if (!dict) {
    emitError() << "expected DictionaryAttr to set properties";
    return ::mlir::failure();
  }

  {
    auto &propStorage = prop.bCluster;
       auto attr = dict.get("bCluster");
    if (attr || /*isRequired=*/true) {
      if (!attr) {
        emitError() << "expected key entry for bCluster in DictionaryAttr to set "
                   "Properties.";
        return ::mlir::failure();
      }
      auto convertedAttr = ::llvm::dyn_cast<std::remove_reference_t<decltype(propStorage)>>(attr);
      if (convertedAttr) {
        propStorage = convertedAttr;
      } else {
        emitError() << "Invalid attribute `bCluster` in property conversion: " << attr;
        return ::mlir::failure();
      }
    }
  }
  return ::mlir::success();
}

::mlir::Attribute FenceAsyncSharedOp::getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop) {
    ::mlir::SmallVector<::mlir::NamedAttribute> attrs;
    ::mlir::Builder odsBuilder{ctx};

    {
      const auto &propStorage = prop.bCluster;
      if (propStorage)
        attrs.push_back(odsBuilder.getNamedAttr("bCluster",
                                       propStorage));
    }

  if (!attrs.empty())
    return odsBuilder.getDictionaryAttr(attrs);
  return {};
}

llvm::hash_code FenceAsyncSharedOp::computePropertiesHash(const Properties &prop) {
  return llvm::hash_combine(
    llvm::hash_value(prop.bCluster.getAsOpaquePointer()));
}

std::optional<mlir::Attribute> FenceAsyncSharedOp::getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name) {
    if (name == "bCluster")
      return prop.bCluster;
  return std::nullopt;
}

void FenceAsyncSharedOp::setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value) {
    if (name == "bCluster") {
       prop.bCluster = ::llvm::dyn_cast_or_null<std::remove_reference_t<decltype(prop.bCluster)>>(value);
       return;
    }
}

void FenceAsyncSharedOp::populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs) {
    if (prop.bCluster) attrs.append("bCluster", prop.bCluster);
}

::mlir::LogicalResult FenceAsyncSharedOp::verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError) {
    {
      ::mlir::Attribute attr = attrs.get(getBClusterAttrName(opName));
      if (attr && ::mlir::failed(__mlir_ods_local_attr_constraint_TritonNvidiaGPUOps1(attr, "bCluster", emitError)))
        return ::mlir::failure();
    }
    return ::mlir::success();
}

::mlir::LogicalResult FenceAsyncSharedOp::readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state) {
  auto &prop = state.getOrAddProperties<Properties>(); (void)prop;
  if (::mlir::failed(reader.readAttribute(prop.bCluster)))
    return ::mlir::failure();
  return ::mlir::success();
}

void FenceAsyncSharedOp::writeProperties(::mlir::DialectBytecodeWriter &writer) {
  auto &prop = getProperties(); (void)prop;
  writer.writeAttribute(prop.bCluster);
}

::mlir::BoolAttr FenceAsyncSharedOp::getBClusterAttr() {
  return ::llvm::cast<::mlir::BoolAttr>(getProperties().bCluster);
}

bool FenceAsyncSharedOp::getBCluster() {
  auto attr = getBClusterAttr();
  return attr.getValue();
}

void FenceAsyncSharedOp::setBClusterAttr(::mlir::BoolAttr attr) {
  getProperties().bCluster = attr;
}

void FenceAsyncSharedOp::setBCluster(bool attrValue) {
  getProperties().bCluster = ::mlir::Builder((*this)->getContext()).getBoolAttr(attrValue);
}

void FenceAsyncSharedOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::BoolAttr bCluster) {
  odsState.getOrAddProperties<Properties>().bCluster = bCluster;
}

void FenceAsyncSharedOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::BoolAttr bCluster) {
  odsState.getOrAddProperties<Properties>().bCluster = bCluster;
  assert(resultTypes.size() == 0u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void FenceAsyncSharedOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, bool bCluster) {
  odsState.getOrAddProperties<Properties>().bCluster = odsBuilder.getBoolAttr(bCluster);
}

void FenceAsyncSharedOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, bool bCluster) {
  odsState.getOrAddProperties<Properties>().bCluster = odsBuilder.getBoolAttr(bCluster);
  assert(resultTypes.size() == 0u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void FenceAsyncSharedOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 0u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 0u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

::mlir::LogicalResult FenceAsyncSharedOp::verifyInvariantsImpl() {
  auto tblgen_bCluster = getProperties().bCluster; (void)tblgen_bCluster;
  if (!tblgen_bCluster) return emitOpError("requires attribute 'bCluster'");

  if (::mlir::failed(__mlir_ods_local_attr_constraint_TritonNvidiaGPUOps1(*this, tblgen_bCluster, "bCluster")))
    return ::mlir::failure();
  return ::mlir::success();
}

::mlir::LogicalResult FenceAsyncSharedOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::ParseResult FenceAsyncSharedOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
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

void FenceAsyncSharedOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
}

} // namespace nvidia_gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::nvidia_gpu::FenceAsyncSharedOp)

namespace mlir {
namespace triton {
namespace nvidia_gpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::nvidia_gpu::GetClusterCTAIdOp definitions
//===----------------------------------------------------------------------===//

namespace detail {
GetClusterCTAIdOpGenericAdaptorBase::GetClusterCTAIdOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const ::mlir::EmptyProperties &properties, ::mlir::RegionRange regions) : odsAttrs(attrs), odsRegions(regions) {  if (odsAttrs)
    odsOpName.emplace("triton_nvidia_gpu.get_cluster_cta_id", odsAttrs.getContext());
}

GetClusterCTAIdOpGenericAdaptorBase::GetClusterCTAIdOpGenericAdaptorBase(GetClusterCTAIdOp op) : GetClusterCTAIdOpGenericAdaptorBase(op->getAttrDictionary(), op.getProperties(), op->getRegions()) {}

std::pair<unsigned, unsigned> GetClusterCTAIdOpGenericAdaptorBase::getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
  return {index, 1};
}

::mlir::DictionaryAttr GetClusterCTAIdOpGenericAdaptorBase::getAttributes() {
  return odsAttrs;
}

} // namespace detail
GetClusterCTAIdOpAdaptor::GetClusterCTAIdOpAdaptor(GetClusterCTAIdOp op) : GetClusterCTAIdOpGenericAdaptor(op->getOperands(), op) {}

::mlir::LogicalResult GetClusterCTAIdOpAdaptor::verify(::mlir::Location loc) {
  return ::mlir::success();
}

std::pair<unsigned, unsigned> GetClusterCTAIdOp::getODSOperandIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::operand_range GetClusterCTAIdOp::getODSOperands(unsigned index) {
  auto valueRange = getODSOperandIndexAndLength(index);
  return {std::next(getOperation()->operand_begin(), valueRange.first),
           std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
}

std::pair<unsigned, unsigned> GetClusterCTAIdOp::getODSResultIndexAndLength(unsigned index) {
  return {index, 1};
}

::mlir::Operation::result_range GetClusterCTAIdOp::getODSResults(unsigned index) {
  auto valueRange = getODSResultIndexAndLength(index);
  return {std::next(getOperation()->result_begin(), valueRange.first),
           std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
}

::mlir::TypedValue<::mlir::IntegerType> GetClusterCTAIdOp::getResult() {
  return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSResults(0).begin());
}

void GetClusterCTAIdOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result) {
  odsState.addTypes(result);
}

void GetClusterCTAIdOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState) {
        ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
        if (::mlir::succeeded(GetClusterCTAIdOp::inferReturnTypes(odsBuilder.getContext(),
                      odsState.location, odsState.operands,
                      odsState.attributes.getDictionary(odsState.getContext()),
                      odsState.getRawProperties(),
                      odsState.regions, inferredReturnTypes)))
          odsState.addTypes(inferredReturnTypes);
        else
          ::llvm::report_fatal_error("Failed to infer result type(s).");
}

void GetClusterCTAIdOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes) {
  assert(resultTypes.size() == 1u && "mismatched number of results");
  odsState.addTypes(resultTypes);
}

void GetClusterCTAIdOp::build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 0u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);
  assert(resultTypes.size() == 1u && "mismatched number of return types");
  odsState.addTypes(resultTypes);
}

void GetClusterCTAIdOp::build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes) {
  assert(operands.size() == 0u && "mismatched number of parameters");
  odsState.addOperands(operands);
  odsState.addAttributes(attributes);

  ::llvm::SmallVector<::mlir::Type, 2> inferredReturnTypes;
  if (::mlir::succeeded(GetClusterCTAIdOp::inferReturnTypes(odsBuilder.getContext(),
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

::mlir::LogicalResult GetClusterCTAIdOp::verifyInvariantsImpl() {
  {
    unsigned index = 0; (void)index;
    auto valueGroup0 = getODSResults(0);

    for (auto v : valueGroup0) {
      if (::mlir::failed(__mlir_ods_local_type_constraint_TritonNvidiaGPUOps3(*this, v.getType(), "result", index++)))
        return ::mlir::failure();
    }
  }
  return ::mlir::success();
}

::mlir::LogicalResult GetClusterCTAIdOp::verifyInvariants() {
  return verifyInvariantsImpl();
}

::mlir::LogicalResult GetClusterCTAIdOp::inferReturnTypes(::mlir::MLIRContext *context, ::std::optional<::mlir::Location> location, ::mlir::ValueRange operands, ::mlir::DictionaryAttr attributes, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions, ::llvm::SmallVectorImpl<::mlir::Type>&inferredReturnTypes) {
  inferredReturnTypes.resize(1);
  ::mlir::Builder odsBuilder(context);
  ::mlir::Type odsInferredType0 = odsBuilder.getIntegerType(32);
  inferredReturnTypes[0] = odsInferredType0;
  return ::mlir::success();
}

::mlir::ParseResult GetClusterCTAIdOp::parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result) {
  ::mlir::Type resultRawTypes[1];
  ::llvm::ArrayRef<::mlir::Type> resultTypes(resultRawTypes);
  {
    auto loc = parser.getCurrentLocation();(void)loc;
    if (parser.parseOptionalAttrDict(result.attributes))
      return ::mlir::failure();
  }
  if (parser.parseColon())
    return ::mlir::failure();

  {
    ::mlir::IntegerType type;
    if (parser.parseCustomTypeWithFallback(type))
      return ::mlir::failure();
    resultRawTypes[0] = type;
  }
  result.addTypes(resultTypes);
  return ::mlir::success();
}

void GetClusterCTAIdOp::print(::mlir::OpAsmPrinter &_odsPrinter) {
  ::llvm::SmallVector<::llvm::StringRef, 2> elidedAttrs;
  _odsPrinter.printOptionalAttrDict((*this)->getAttrs(), elidedAttrs);
  _odsPrinter << ' ' << ":";
  _odsPrinter << ' ';
  {
    auto type = getResult().getType();
    if (auto validType = ::llvm::dyn_cast<::mlir::IntegerType>(type))
      _odsPrinter.printStrippedAttrOrType(validType);
   else
     _odsPrinter << type;
  }
}

void GetClusterCTAIdOp::getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects) {
}

} // namespace nvidia_gpu
} // namespace triton
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::triton::nvidia_gpu::GetClusterCTAIdOp)


#endif  // GET_OP_CLASSES

